"""
Student Dashboard Flask Application

A production-ready Flask application for managing student data with filtering,
export capabilities, and database operations.

Features:
- Student data import from Excel
- Advanced filtering (age, class, gender)
- Excel export functionality
- SQLite database with proper error handling
- Clean modular architecture
"""
from flask import Flask, render_template, redirect, url_for, request, flash
import config
import models
import utils

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def home():
    """
    Home page - displays student data with current filters.
    Loads initial data from database if available.
    """
    try:
        # Get all students and add age
        rows = models.get_all_students()
        data_with_age = utils.add_age_to_students(rows)
        
        # Apply default filters (all)
        filtered_data = utils.apply_filters(
            data_with_age,
            class_filter='all',
            gender_filter='all'
        )
        
        # Calculate summary
        summary = utils.calculate_summary(filtered_data)
        
        return render_template(
            'home.html',
            data=filtered_data,
            data_all=summary['all'],
            data_male=summary['male'],
            data_female=summary['female'],
            age='',
            age_1='',
            age_2='',
            class_html='all',
            gender='all',
            message='',
            message_type=''
        )
    except Exception as e:
        app.logger.error(f"Error loading home page: {e}")
        return render_template('home.html', **utils.get_default_context())


@app.route('/insert', methods=['POST'])
def insert_data():
    """
    Import student data from Excel file to database.
    Reads from configured input path and inserts into SQLite.
    """
    try:
        # Read Excel file
        student_data = utils.read_excel_students(str(config.EXCEL_PATH_INPUT))
        
        if not student_data:
            flash('No data found in Excel file', 'error')
            return redirect(url_for('home'))
        
        # Bulk insert students
        success_count, fail_count = models.bulk_insert_students(student_data)
        
        if success_count > 0:
            flash(f'Successfully imported {success_count} students', 'success')
        if fail_count > 0:
            flash(f'{fail_count} records skipped (duplicates)', 'warning')
            
    except FileNotFoundError:
        flash('Input Excel file not found', 'error')
    except ValueError as e:
        flash(f'Error reading Excel file: {e}', 'error')
    except Exception as e:
        app.logger.error(f"Error inserting data: {e}")
        flash('An error occurred while importing data', 'error')
    
    return redirect(url_for('home'))


@app.route('/view_tb', methods=['POST'])
def view_data():
    """
    Handle filter and export actions from the dashboard.
    Supports: Run filters, Export to Excel
    """
    try:
        # Get form parameters
        age_single = request.form.get('age', type=int)
        age_min = request.form.get('age_1', type=int)
        age_max = request.form.get('age_2', type=int)
        class_filter = request.form.get('class', 'all')
        gender_filter = request.form.get('gender', 'all')
        filename = request.form.get('file_name', '').strip()
        action = request.form.get('on')
        
        # Get all students from database
        rows = models.get_all_students()
        data_with_age = utils.add_age_to_students(rows)
        
        # Apply filters
        filtered_data = utils.apply_filters(
            data_with_age,
            class_filter=class_filter,
            gender_filter=gender_filter,
            age_single=age_single,
            age_min=age_min,
            age_max=age_max
        )
        
        # Calculate summary
        summary = utils.calculate_summary(filtered_data)
        
        # Handle actions
        if action == 'run':
            # Display filtered data
            return render_template(
                'home.html',
                data=filtered_data,
                data_all=summary['all'],
                data_male=summary['male'],
                data_female=summary['female'],
                age=request.form.get('age', ''),
                age_1=request.form.get('age_1', ''),
                age_2=request.form.get('age_2', ''),
                class_html=class_filter,
                gender=gender_filter,
                message='',
                message_type=''
            )
            
        elif action == 'save_file':
            # Export to Excel
            if not filename:
                flash('Please enter a file name', 'warning')
                return render_template(
                    'home.html',
                    data=filtered_data,
                    data_all=summary['all'],
                    data_male=summary['male'],
                    data_female=summary['female'],
                    age=request.form.get('age', ''),
                    age_1=request.form.get('age_1', ''),
                    age_2=request.form.get('age_2', ''),
                    class_html=class_filter,
                    gender=gender_filter,
                    message='Please enter a file name',
                    message_type='warning'
                )
            
            # Create output path
            output_path = config.EXCEL_OUTPUT_DIR / f"{filename}.xlsx"
            
            # Export data
            success = utils.export_to_excel(
                filtered_data,
                str(output_path),
                include_class=True
            )
            
            if success:
                flash(f'Successfully exported to {filename}.xlsx', 'success')
            else:
                flash('Failed to export file', 'error')
            
            return render_template(
                'home.html',
                data=filtered_data,
                data_all=summary['all'],
                data_male=summary['male'],
                data_female=summary['female'],
                age=request.form.get('age', ''),
                age_1=request.form.get('age_1', ''),
                age_2=request.form.get('age_2', ''),
                class_html=class_filter,
                gender=gender_filter,
                message=f'Exported: {filename}.xlsx' if success else 'Export failed',
                message_type='success' if success else 'error'
            )
        
        # Default: show all data
        return redirect(url_for('home'))
        
    except Exception as e:
        app.logger.error(f"Error in view_data: {e}")
        flash('An error occurred', 'error')
        return redirect(url_for('home'))


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('home.html', **utils.get_default_context()), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    app.logger.error(f"Server error: {e}")
    return render_template('home.html', **utils.get_default_context()), 500


# ============================================================================
# Main
# ============================================================================

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)