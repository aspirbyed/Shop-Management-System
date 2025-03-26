import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from matplotlib.table import Table
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class SalesAnalyzer:
    def __init__(self, db_path="sms.db"):
        """Initialize the SalesAnalyzer with the database path and load data."""
        self.db_path = db_path
        self.sales_df = None
        self.sale_details_df = None
        self.product_df = None
        # Place the report directory inside the user's Documents folder
        documents_dir = os.path.expanduser("~/Documents")
        self.report_dir = os.path.join(documents_dir, "report")
        self.output_dirs = {
            'day': os.path.join(self.report_dir, 'day'),
            'month': os.path.join(self.report_dir, 'month'),
            'year': os.path.join(self.report_dir, 'year')
        }
        self.create_output_dirs()
        self.load_data_from_db()

    def create_output_dirs(self):
        """Create the report directory and subdirectories for day, month, and year if they don't exist."""
        # Create the report directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
            print(f"Created directory: {self.report_dir}")

        # Create subdirectories for day, month, and year
        for dir_path in self.output_dirs.values():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")

    def load_data_from_db(self):
        """Load data from the SQLite database and preprocess it."""
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            print(f"Successfully connected to the database: {self.db_path}")

            # Fetch Sales data
            sales_query = "SELECT * FROM Sales"
            self.sales_df = pd.read_sql_query(sales_query, conn)

            # Fetch SaleDetails data
            sale_details_query = "SELECT * FROM SaleDetails"
            self.sale_details_df = pd.read_sql_query(sale_details_query, conn)

            # Fetch Product data
            product_query = "SELECT * FROM Product"
            self.product_df = pd.read_sql_query(product_query, conn)

            # Close the connection
            conn.close()
            print("Database connection closed.")

            # Convert SaleDate to datetime and extract the date part
            self.sales_df['SaleDate'] = pd.to_datetime(self.sales_df['SaleDate'])
            self.sales_df['Date'] = self.sales_df['SaleDate'].dt.date
            self.sales_df['YearMonth'] = self.sales_df['SaleDate'].dt.to_period('M')  # e.g., 2025-03
            self.sales_df['Year'] = self.sales_df['SaleDate'].dt.year  # e.g., 2025
            self.sales_df['MonthName'] = self.sales_df['SaleDate'].dt.strftime('%B')  # e.g., March
            self.sales_df['MonthNumber'] = self.sales_df['SaleDate'].dt.month  # e.g., 3 for March

        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            exit(1)
        except Exception as e:
            print(f"Error loading data from database: {str(e)}")
            exit(1)

    def save_and_show_plot(self, fig, filename, analysis_type):
        """Save the plot to the appropriate directory and display it."""
        try:
            output_dir = self.output_dirs[analysis_type]
            filepath = os.path.join(output_dir, filename)
            fig.savefig(filepath, bbox_inches='tight')
            print(f"Saved plot: {filepath}")
            plt.show()
        except Exception as e:
            print(f"Error saving plot {filename}: {str(e)}")
        finally:
            plt.close(fig)

    def create_summary_table(self, data, title, time_frame_str, analysis_type):
        """Create a table visualization for summary data and save it."""
        try:
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.axis('off')  # Hide axes
            table_data = [list(data.keys()), list(data.values())]
            table = Table(ax, bbox=[0, 0, 1, 1])
            n_rows, n_cols = 2, len(data)
            for i in range(n_rows):
                for j in range(n_cols):
                    table.add_cell(i, j, 1, 1, text=table_data[i][j], loc='center')
            ax.add_table(table)
            plt.title(f"{title} for {time_frame_str}")
            plt.tight_layout()
            filename = f"{title.replace(' ', '_').lower()}_{time_frame_str.replace(' ', '_')}.png"
            self.save_and_show_plot(fig, filename, analysis_type)
        except Exception as e:
            print(f"Error creating summary table: {str(e)}")

    def create_product_sales_table(self, product_sales, title, time_frame_str, analysis_type):
        """Create a table visualization for product sales data and save it."""
        try:
            fig, ax = plt.subplots(figsize=(10, len(product_sales) * 0.5 + 1))
            ax.axis('off')  # Hide axes
            table_data = [product_sales.columns.tolist()] + product_sales.values.tolist()
            table = Table(ax, bbox=[0, 0, 1, 1])
            n_rows, n_cols = len(table_data), len(table_data[0])
            for i in range(n_rows):
                for j in range(n_cols):
                    table.add_cell(i, j, 1, 1, text=table_data[i][j], loc='center')
            ax.add_table(table)
            plt.title(f"{title} in {time_frame_str}")
            plt.tight_layout()
            filename = f"{title.replace(' ', '_').lower()}_{time_frame_str.replace(' ', '_')}.png"
            self.save_and_show_plot(fig, filename, analysis_type)
        except Exception as e:
            print(f"Error creating product sales table: {str(e)}")

    def plot_monthly_sales(self, monthly_sales, target_year):
        """Create a bar plot for monthly sales in yearly analysis and save it."""
        try:
            fig = plt.figure(figsize=(10, 6))
            sns.barplot(x='TotalSales', y='MonthName', hue='MonthName', data=monthly_sales, palette='Blues_d', legend=False)
            plt.title(f'Monthly Sales Breakdown for {target_year}')
            plt.xlabel('Total Sales ($)')
            plt.ylabel('Month')
            plt.tight_layout()
            filename = f"monthly_sales_breakdown_{target_year}.png"
            self.save_and_show_plot(fig, filename, 'year')
        except Exception as e:
            print(f"Error plotting monthly sales breakdown: {str(e)}")

    def generate_visualizations(self, product_sales, time_frame_str, analysis_type):
        """Generate visualizations for product sales and save them."""
        try:
            # Determine the number of unique products sold
            num_products = len(product_sales)
            print(f"Number of unique products sold: {num_products}")

            # Show all distinct products for tables and histograms
            top_n = num_products
            print(f"Showing all {top_n} distinct products sold in {time_frame_str} (for tables and histograms).")

            # Sort by quantity sold
            top_products_by_quantity = product_sales.sort_values(by='Quantity', ascending=False)

            # Sort by revenue (Subtotal)
            top_products_by_revenue = product_sales.sort_values(by='Subtotal', ascending=False)

            # Create table visualizations for product sales data
            self.create_product_sales_table(top_products_by_quantity, "Products by Quantity Sold", time_frame_str, analysis_type)
            self.create_product_sales_table(top_products_by_revenue, "Products by Revenue", time_frame_str, analysis_type)

            # Set up the plotting style
            sns.set(style="whitegrid")

            # Histogram 1: Products by Quantity Sold
            try:
                fig = plt.figure(figsize=(10, len(top_products_by_quantity) * 0.5 + 1))
                sns.barplot(x='Quantity', y='ProductName', hue='ProductName', data=top_products_by_quantity, palette='Blues_d', legend=False)
                plt.title(f'Products by Quantity Sold in {time_frame_str}')
                plt.xlabel('Quantity Sold')
                plt.ylabel('Product Name')
                plt.tight_layout()
                filename = f"products_by_quantity_sold_{time_frame_str.replace(' ', '_')}.png"
                self.save_and_show_plot(fig, filename, analysis_type)
            except Exception as e:
                print(f"Error plotting histogram for quantity sold: {str(e)}")

            # Histogram 2: Products by Revenue
            try:
                fig = plt.figure(figsize=(10, len(top_products_by_revenue) * 0.5 + 1))
                sns.barplot(x='Subtotal', y='ProductName', hue='ProductName', data=top_products_by_revenue, palette='Greens_d', legend=False)
                plt.title(f'Products by Revenue in {time_frame_str}')
                plt.xlabel('Revenue ($)')
                plt.ylabel('Product Name')
                plt.tight_layout()
                filename = f"products_by_revenue_{time_frame_str.replace(' ', '_')}.png"
                self.save_and_show_plot(fig, filename, analysis_type)
            except Exception as e:
                print(f"Error plotting histogram for revenue: {str(e)}")

            # Pie Chart: Top 5 Products by Quantity Sold, with "Others" category
            try:
                max_pie_products = 5
                if num_products > max_pie_products:
                    top_5_products = top_products_by_quantity.head(max_pie_products)
                    others_quantity = top_products_by_quantity['Quantity'].iloc[max_pie_products:].sum()
                    pie_data = pd.DataFrame({
                        'ProductName': list(top_5_products['ProductName']) + ['Others'],
                        'Quantity': list(top_5_products['Quantity']) + [others_quantity]
                    })
                else:
                    pie_data = top_products_by_quantity

                fig = plt.figure(figsize=(8, 8))
                plt.pie(pie_data['Quantity'], labels=pie_data['ProductName'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('Pastel1'))
                plt.title(f'Distribution of Top Products by Quantity Sold in {time_frame_str} (Top 5, Others Combined)')
                plt.tight_layout()
                filename = f"distribution_by_quantity_sold_{time_frame_str.replace(' ', '_')}.png"
                self.save_and_show_plot(fig, filename, analysis_type)
            except Exception as e:
                print(f"Error plotting pie chart: {str(e)}")

        except Exception as e:
            print(f"An unexpected error occurred during visualization: {str(e)}")

    def analyze_sales_for_day(self, target_date):
        """Analyze sales for a specific day."""
        try:
            target_date_str = target_date
            daily_sales = self.sales_df[self.sales_df['Date'].astype(str) == target_date_str]

            if daily_sales.empty:
                print(f"No sales found for {target_date_str}")
                return False

            total_sales = daily_sales['TotalAmount'].sum()
            num_transactions = len(daily_sales)

            summary_data = {
                "Total Sales ($)": f"{total_sales:.2f}",
                "Number of Transactions": num_transactions
            }
            self.create_summary_table(summary_data, "Daily Sales Summary", target_date_str, 'day')

            daily_sale_details = self.sale_details_df[self.sale_details_df['SalesID'].isin(daily_sales['SalesID'])]
            if daily_sale_details.empty:
                print("No sale details found for the selected date.")
                return False

            daily_sale_details = daily_sale_details.merge(self.product_df[['ProductID', 'ProductName']], on='ProductID')
            if daily_sale_details.empty:
                print("No matching products found in sale details.")
                return False

            product_sales = daily_sale_details.groupby(['ProductID', 'ProductName']).agg({
                'Quantity': 'sum',
                'Subtotal': 'sum'
            }).reset_index()

            if product_sales.empty:
                print("No products sold on the selected date.")
                return False

            self.generate_visualizations(product_sales, target_date_str, 'day')
            return True

        except Exception as e:
            print(f"An unexpected error occurred during daily analysis: {str(e)}")
            return False

    def analyze_sales_for_month(self, target_year_month):
        """Analyze sales for a specific month."""
        try:
            target_year_month_str = target_year_month
            monthly_sales = self.sales_df[self.sales_df['YearMonth'].astype(str) == target_year_month_str]

            if monthly_sales.empty:
                print(f"No sales found for {target_year_month_str}")
                return False

            total_sales = monthly_sales['TotalAmount'].sum()
            num_transactions = len(monthly_sales)

            summary_data = {
                "Total Sales ($)": f"{total_sales:.2f}",
                "Number of Transactions": num_transactions
            }
            self.create_summary_table(summary_data, "Monthly Sales Summary", target_year_month_str, 'month')

            monthly_sale_details = self.sale_details_df[self.sale_details_df['SalesID'].isin(monthly_sales['SalesID'])]
            if monthly_sale_details.empty:
                print("No sale details found for the selected month.")
                return False

            monthly_sale_details = monthly_sale_details.merge(self.product_df[['ProductID', 'ProductName']], on='ProductID')
            if monthly_sale_details.empty:
                print("No matching products found in sale details.")
                return False

            product_sales = monthly_sale_details.groupby(['ProductID', 'ProductName']).agg({
                'Quantity': 'sum',
                'Subtotal': 'sum'
            }).reset_index()

            if product_sales.empty:
                print("No products sold in the selected month.")
                return False

            self.generate_visualizations(product_sales, target_year_month_str, 'month')
            return True

        except Exception as e:
            print(f"An unexpected error occurred during monthly analysis: {str(e)}")
            return False

    def analyze_sales_for_year(self, target_year):
        """Analyze sales for a specific year."""
        try:
            target_year_int = int(target_year)
            yearly_sales = self.sales_df[self.sales_df['Year'] == target_year_int]

            if yearly_sales.empty:
                print(f"No sales found for {target_year}")
                return False

            total_sales = yearly_sales['TotalAmount'].sum()
            num_transactions = len(yearly_sales)

            summary_data = {
                "Total Sales ($)": f"{total_sales:.2f}",
                "Number of Transactions": num_transactions
            }
            self.create_summary_table(summary_data, "Yearly Sales Summary", str(target_year), 'year')

            all_months = pd.DataFrame({
                'MonthName': ['January', 'February', 'March', 'April', 'May', 'June', 
                              'July', 'August', 'September', 'October', 'November', 'December'],
                'MonthNumber': range(1, 13)
            })

            monthly_sales = yearly_sales.groupby(['MonthName', 'MonthNumber'])['TotalAmount'].sum().reset_index()
            monthly_sales = monthly_sales.rename(columns={'TotalAmount': 'TotalSales'})
            monthly_sales = all_months.merge(monthly_sales, on=['MonthName', 'MonthNumber'], how='left')
            monthly_sales['TotalSales'] = monthly_sales['TotalSales'].fillna(0)
            monthly_sales = monthly_sales.sort_values('MonthNumber')

            self.plot_monthly_sales(monthly_sales, target_year)

            yearly_sale_details = self.sale_details_df[self.sale_details_df['SalesID'].isin(yearly_sales['SalesID'])]
            if yearly_sale_details.empty:
                print("No sale details found for the selected year.")
                return False

            yearly_sale_details = yearly_sale_details.merge(self.product_df[['ProductID', 'ProductName']], on='ProductID')
            if yearly_sale_details.empty:
                print("No matching products found in sale details.")
                return False

            product_sales = yearly_sale_details.groupby(['ProductID', 'ProductName']).agg({
                'Quantity': 'sum',
                'Subtotal': 'sum'
            }).reset_index()

            if product_sales.empty:
                print("No products sold in the selected year.")
                return False

            self.generate_visualizations(product_sales, str(target_year), 'year')
            return True

        except Exception as e:
            print(f"An unexpected error occurred during yearly analysis: {str(e)}")
            return False

    def generate_pdf(self, analysis_type, time_frame_str):
        """Generate a PDF file containing all images from the specified analysis type directory and delete the images."""
        try:
            output_dir = self.output_dirs[analysis_type]
            # Save the PDF in the same directory as the images
            pdf_filename = os.path.join(output_dir, f"{analysis_type}_report_{time_frame_str.replace(' ', '_')}.pdf")
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            page_width, page_height = letter

            # Add a title page
            # Determine the title based on analysis type
            if analysis_type == 'day':
                title = f"Daily Report for {time_frame_str}"
            elif analysis_type == 'month':
                # Convert YYYY-MM to Month YYYY (e.g., 2025-03 to March 2025)
                month_year = datetime.strptime(time_frame_str, '%Y-%m')
                title = f"Monthly Report for {month_year.strftime('%B %Y')}"
            else:  # analysis_type == 'year'
                title = f"Yearly Report for {time_frame_str}"

            # Company information and generation date/time
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')

            # Draw the title page
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(page_width / 2, page_height - 50, title)

            c.setFont("Helvetica", 12)
            c.drawCentredString(page_width / 2, page_height - 80, "Company Inc.")
            c.drawCentredString(page_width / 2, page_height - 100, "1234 Fake Street, Imaginary City, IC 56789")
            c.drawCentredString(page_width / 2, page_height - 120, f"Date: {current_date}")
            c.drawCentredString(page_width / 2, page_height - 140, f"Time: {current_time}")

            c.showPage()  # End the title page

            # Get all image files in the directory
            image_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            if not image_files:
                print(f"No images found in {output_dir} to include in the PDF.")
                c.save()
                return

            for image_file in image_files:
                image_path = os.path.join(output_dir, image_file)
                img = ImageReader(image_path)
                img_width, img_height = img.getSize()

                # Scale the image to fit the page while maintaining aspect ratio
                aspect = img_height / float(img_width)
                if (page_width / img_width) < (page_height / img_height):
                    scaled_width = page_width - 40  # Leave some margin
                    scaled_height = scaled_width * aspect
                else:
                    scaled_height = page_height - 40  # Leave some margin
                    scaled_width = scaled_height / aspect

                # Center the image on the page
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2

                c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
                c.showPage()

            c.save()
            print(f"Generated PDF: {pdf_filename}")

            # Delete all images in the directory after creating the PDF
            for image_file in image_files:
                image_path = os.path.join(output_dir, image_file)
                os.remove(image_path)
                print(f"Deleted image: {image_path}")

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

    def main(self, target_date, target_year_month, target_year, analysis_type):
        """Run the sales analysis for the specified analysis type."""
        if analysis_type not in ['day', 'month', 'year']:
            print(f"Invalid analysis type: {analysis_type}. Must be 'day', 'month', or 'year'.")
            return

        # Clear the output directory for the analysis type to avoid including old images in the PDF
        output_dir = self.output_dirs[analysis_type]
        for file in os.listdir(output_dir):
            if file.endswith('.png'):
                os.remove(os.path.join(output_dir, file))
                print(f"Removed old file: {file}")

        # Perform the analysis based on the type
        success = False
        time_frame_str = ""
        if analysis_type == 'day':
            success = self.analyze_sales_for_day(target_date)
            time_frame_str = target_date
        elif analysis_type == 'month':
            success = self.analyze_sales_for_month(target_year_month)
            time_frame_str = target_year_month
        elif analysis_type == 'year':
            success = self.analyze_sales_for_year(target_year)
            time_frame_str = target_year

        # Generate PDF if the analysis was successful
        if success:
            self.generate_pdf(analysis_type, time_frame_str)

if __name__ == '__main__':
    # Example values for testing when running directly
    target_date = '2025-03-01'
    target_year_month = '2025-03'
    target_year = '2025'
    analysis_type = 'day'  # Change to 'month' or 'year' for testing

    analyzer = SalesAnalyzer(db_path="sms.db")
    analyzer.main(target_date, target_year_month, target_year, analysis_type)