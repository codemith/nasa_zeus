"""
Data Visualization Script for Air Quality Dataset
=================================================
Analyzes and visualizes the collected air quality data.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Configuration
DATA_FILE = Path("data/air_quality_dataset.csv")


def load_data():
    """Load the collected air quality dataset."""
    if not DATA_FILE.exists():
        print(f"❌ Data file not found: {DATA_FILE}")
        print("Run: python collect_air_quality_data.py")
        return None
    
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    print(f"✓ Loaded {len(df)} records from {DATA_FILE}")
    return df


def print_summary(df):
    """Print summary statistics."""
    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    
    print(f"\n📅 Date Range:")
    print(f"   From: {df['timestamp'].min()}")
    print(f"   To:   {df['timestamp'].max()}")
    print(f"   Duration: {(df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600:.1f} hours")
    
    print(f"\n📍 Locations:")
    unique_locations = df.groupby(['latitude', 'longitude']).size().reset_index(name='count')
    for _, row in unique_locations.iterrows():
        print(f"   ({row['latitude']:.4f}, {row['longitude']:.4f}): {row['count']} records")
    
    print(f"\n🔬 Data Sources:")
    for source in df['source'].unique():
        count = len(df[df['source'] == source])
        print(f"   {source}: {count} records")
    
    print(f"\n☁️ Pollutants:")
    for param in df['parameter'].unique():
        count = len(df[df['parameter'] == param])
        avg_value = df[df['parameter'] == param]['value'].mean()
        unit = df[df['parameter'] == param]['unit'].iloc[0]
        print(f"   {param:8s}: {count:4d} records, avg={avg_value:8.2f} {unit}")
    
    print(f"\n🌡️ Weather Context:")
    if df['temperature'].notna().any():
        print(f"   Temperature: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
        print(f"   Humidity:    {df['humidity'].min():.0f}% to {df['humidity'].max():.0f}%")
        print(f"   Wind Speed:  {df['wind_speed'].min():.1f} to {df['wind_speed'].max():.1f} m/s")
    else:
        print("   (No weather data available)")
    
    print(f"\n📊 AQI Distribution:")
    if df['aqi'].notna().any():
        aqi_counts = df['aqi'].value_counts().sort_index()
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        for aqi_val, count in aqi_counts.items():
            pct = (count / df['aqi'].notna().sum()) * 100
            print(f"   AQI {aqi_val} ({aqi_labels.get(int(aqi_val), 'Unknown')}): {count} records ({pct:.1f}%)")
    else:
        print("   (No AQI data available)")


def plot_pollutant_trends(df):
    """Plot pollutant concentration trends over time."""
    print("\n📈 Generating pollutant trend charts...")
    
    # Get unique parameters
    parameters = df['parameter'].unique()
    
    # Create figure with subplots
    n_params = len(parameters)
    fig, axes = plt.subplots(n_params, 1, figsize=(12, 3 * n_params), sharex=True)
    
    if n_params == 1:
        axes = [axes]
    
    for ax, param in zip(axes, parameters):
        param_data = df[df['parameter'] == param].sort_values('timestamp')
        
        if len(param_data) > 0:
            ax.plot(param_data['timestamp'], param_data['value'], marker='o', markersize=2)
            ax.set_ylabel(f"{param} ({param_data['unit'].iloc[0]})")
            ax.set_title(f"{param} Concentration Over Time")
            ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time')
    plt.tight_layout()
    plt.savefig('data/pollutant_trends.png', dpi=150)
    print(f"✓ Saved: data/pollutant_trends.png")


def plot_aqi_distribution(df):
    """Plot AQI distribution."""
    if df['aqi'].notna().any():
        print("\n📊 Generating AQI distribution chart...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        aqi_counts = df['aqi'].value_counts().sort_index()
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        
        colors = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97']
        
        bars = ax.bar(
            [aqi_labels.get(int(x), str(x)) for x in aqi_counts.index],
            aqi_counts.values,
            color=[colors[int(x)-1] for x in aqi_counts.index if int(x) <= 5]
        )
        
        ax.set_xlabel('Air Quality Index')
        ax.set_ylabel('Number of Records')
        ax.set_title('AQI Distribution')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('data/aqi_distribution.png', dpi=150)
        print(f"✓ Saved: data/aqi_distribution.png")


def plot_pollutant_correlation(df):
    """Plot correlation matrix for pollutants."""
    print("\n🔗 Generating pollutant correlation matrix...")
    
    # Pivot data to have pollutants as columns
    pivot_df = df.pivot_table(
        values='value',
        index='timestamp',
        columns='parameter',
        aggfunc='mean'
    )
    
    if len(pivot_df.columns) > 1:
        correlation = pivot_df.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(correlation, cmap='coolwarm', vmin=-1, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(correlation.columns)))
        ax.set_yticks(range(len(correlation.columns)))
        ax.set_xticklabels(correlation.columns, rotation=45, ha='right')
        ax.set_yticklabels(correlation.columns)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient')
        
        # Add correlation values
        for i in range(len(correlation.columns)):
            for j in range(len(correlation.columns)):
                text = ax.text(j, i, f'{correlation.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=10)
        
        ax.set_title('Pollutant Correlation Matrix')
        plt.tight_layout()
        plt.savefig('data/pollutant_correlation.png', dpi=150)
        print(f"✓ Saved: data/pollutant_correlation.png")


def export_summary_report(df):
    """Export a text summary report."""
    print("\n📄 Generating summary report...")
    
    report_file = Path("data/analysis_report.txt")
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AIR QUALITY DATA ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Records: {len(df)}\n")
        f.write(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}\n\n")
        
        f.write("Data Sources:\n")
        for source in df['source'].unique():
            count = len(df[df['source'] == source])
            f.write(f"  - {source}: {count} records\n")
        f.write("\n")
        
        f.write("Pollutant Statistics:\n")
        for param in df['parameter'].unique():
            param_data = df[df['parameter'] == param]
            f.write(f"\n{param}:\n")
            f.write(f"  Count:   {len(param_data)}\n")
            f.write(f"  Mean:    {param_data['value'].mean():.2f} {param_data['unit'].iloc[0]}\n")
            f.write(f"  Std Dev: {param_data['value'].std():.2f}\n")
            f.write(f"  Min:     {param_data['value'].min():.2f}\n")
            f.write(f"  Max:     {param_data['value'].max():.2f}\n")
        
        if df['aqi'].notna().any():
            f.write("\nAir Quality Index Distribution:\n")
            aqi_counts = df['aqi'].value_counts().sort_index()
            aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            for aqi_val, count in aqi_counts.items():
                pct = (count / df['aqi'].notna().sum()) * 100
                f.write(f"  AQI {aqi_val} ({aqi_labels.get(int(aqi_val), 'Unknown')}): {count} ({pct:.1f}%)\n")
    
    print(f"✓ Saved: {report_file}")


def main():
    """Main analysis function."""
    print("\n" + "=" * 80)
    print("AIR QUALITY DATA ANALYSIS")
    print("=" * 80)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Print summary
    print_summary(df)
    
    # Generate visualizations
    try:
        plot_pollutant_trends(df)
        plot_aqi_distribution(df)
        plot_pollutant_correlation(df)
        export_summary_report(df)
        
        print("\n" + "=" * 80)
        print("✓ ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - data/pollutant_trends.png")
        print("  - data/aqi_distribution.png")
        print("  - data/pollutant_correlation.png")
        print("  - data/analysis_report.txt")
        print("\n")
    
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
        print("Note: matplotlib required. Install with: pip install matplotlib")


if __name__ == "__main__":
    main()
