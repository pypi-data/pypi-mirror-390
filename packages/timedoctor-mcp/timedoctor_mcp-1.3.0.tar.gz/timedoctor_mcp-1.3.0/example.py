"""
Example Usage of Time Doctor Scraper

This script demonstrates how to use the Time Doctor scraper
both as a standalone tool and through its components.
"""

import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import TimeDoctorScraper
from parser import TimeDoctorParser
from transformer import export_to_csv, get_hours_summary, TimeDoctorTransformer


async def example_1_daily_report():
    """Example 1: Get today's report and display it."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Get Today's Time Tracking Report")
    print("="*60 + "\n")

    scraper = TimeDoctorScraper()
    parser = TimeDoctorParser()
    transformer = TimeDoctorTransformer()

    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"Fetching report for: {today}\n")

        # Get report data
        data = await scraper.get_report_data(today)

        if data['success']:
            # Parse HTML
            entries = parser.parse_daily_report(data['html'], today)
            entries = parser.aggregate_by_task(entries)

            # Transform and display
            transformed = transformer.transform_entries(entries)

            if transformed:
                print(f"Found {len(transformed)} time entries:\n")

                for entry in transformed:
                    print(f"  Project: {entry['Project']}")
                    print(f"  Task: {entry['Task']}")
                    print(f"  Description: {entry['Description']}")
                    print(f"  Hours: {entry['WORK HOUR']:.2f}")
                    print()

                total = transformer.calculate_total(transformed)
                print(f"Total Hours: {total:.2f}\n")
            else:
                print("No time entries found for today.\n")
        else:
            print("Failed to fetch report.\n")

    except Exception as e:
        print(f"Error: {e}\n")


async def example_2_export_csv():
    """Example 2: Export today's report to CSV."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Export Today's Report to CSV")
    print("="*60 + "\n")

    scraper = TimeDoctorScraper()
    parser = TimeDoctorParser()

    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        output_file = f"report_{today}.csv"

        print(f"Exporting report for {today} to {output_file}...\n")

        # Get report data
        data = await scraper.get_report_data(today)

        if data['success']:
            # Parse HTML
            entries = parser.parse_daily_report(data['html'], today)
            entries = parser.aggregate_by_task(entries)

            # Export to CSV
            csv_path = export_to_csv(entries, output_file)

            print(f"✓ Successfully exported to: {csv_path}")
            print(f"  Entries: {len(entries)}")

            # Show summary
            summary = get_hours_summary(entries)
            print(f"\nHours by Project:")
            for project, hours in summary.items():
                print(f"  {project}: {hours:.2f} hours")

            total = sum(summary.values())
            print(f"\nTotal: {total:.2f} hours\n")
        else:
            print("Failed to fetch report.\n")

    except Exception as e:
        print(f"Error: {e}\n")


async def example_3_weekly_report():
    """Example 3: Export weekly report (last 7 days)."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Export Weekly Report (Last 7 Days)")
    print("="*60 + "\n")

    scraper = TimeDoctorScraper()
    parser = TimeDoctorParser()
    transformer = TimeDoctorTransformer()

    try:
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        output_file = f"weekly_report_{start_str}_to_{end_str}.csv"

        print(f"Date Range: {start_str} to {end_str}")
        print(f"Output File: {output_file}\n")

        # Get weekly data
        weekly_data = await scraper.get_weekly_data(start_str, end_str)

        # Parse all entries
        all_entries = []
        for day_data in weekly_data:
            if day_data['success']:
                entries = parser.parse_daily_report(day_data['html'], day_data['date'])
                all_entries.extend(entries)

        # Aggregate
        all_entries = parser.aggregate_by_task(all_entries)

        print(f"Fetched data for {len(weekly_data)} days")
        print(f"Total entries: {len(all_entries)}\n")

        # Export to CSV
        csv_path = export_to_csv(all_entries, output_file)

        print(f"✓ Successfully exported to: {csv_path}\n")

        # Show summary by project
        summary = get_hours_summary(all_entries)
        print("Weekly Hours by Project:")
        print("-" * 40)
        for project, hours in sorted(summary.items(), key=lambda x: x[1], reverse=True):
            print(f"  {project:.<30} {hours:>6.2f}h")

        total = sum(summary.values())
        print("-" * 40)
        print(f"  {'TOTAL':.<30} {total:>6.2f}h\n")

    except Exception as e:
        print(f"Error: {e}\n")


async def example_4_hours_summary():
    """Example 4: Get quick hours summary."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Quick Hours Summary")
    print("="*60 + "\n")

    scraper = TimeDoctorScraper()
    parser = TimeDoctorParser()
    transformer = TimeDoctorTransformer()

    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        print(f"Getting hours summary for: {today}\n")

        # Get report data
        data = await scraper.get_report_data(today)

        if data['success']:
            # Parse HTML
            entries = parser.parse_daily_report(data['html'], today)
            entries = parser.aggregate_by_task(entries)

            # Get summary
            summary = get_hours_summary(entries)

            # Format and display
            summary_text = transformer.format_summary_text(summary)
            print(summary_text)
            print()
        else:
            print("Failed to fetch report.\n")

    except Exception as e:
        print(f"Error: {e}\n")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("TIME DOCTOR SCRAPER - EXAMPLES")
    print("="*60)

    # Check if credentials are configured
    from dotenv import load_dotenv
    load_dotenv()

    email = os.getenv('TD_EMAIL')
    password = os.getenv('TD_PASSWORD')

    if not email or not password or email == 'user@example.com':
        print("\n⚠️  WARNING: Please configure your credentials in .env file")
        print("   Edit .env and set TD_EMAIL and TD_PASSWORD\n")
        print("="*60 + "\n")
        return

    print("\nRunning examples...\n")

    # Run examples
    try:
        # Example 1: Display today's report
        await example_1_daily_report()

        # Example 2: Export to CSV
        await example_2_export_csv()

        # Example 3: Weekly report
        # Uncomment to run (takes longer)
        # await example_3_weekly_report()

        # Example 4: Hours summary
        await example_4_hours_summary()

        print("="*60)
        print("All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
