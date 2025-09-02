# 3D Bolt Dataset Generator (Fusion 360)

## Overview
This project generates a large, labeled 3D dataset of metric hex-head bolts as STL files using Autodesk Fusion 360's scripting interface. It automates the creation of unique bolt geometries with realistic head/body features and threads, exporting them as STL files for machine learning applications.

**Note**: This project focused on dataset generation; ML model training (PointNet/PointNeXt) is planned for future work.

## Features
- **Batch Generation**: Creates 250 bolts per run to avoid Fusion 360 stability issues
- **Progress Tracking**: Crash-safe resume functionality via JSON tracking files
- **Unique Bolts**: Ensures each generated bolt has distinct dimensions from the dataset
- **STL Export**: High-quality mesh export with medium refinement
- **Thread Modeling**: Realistic thread generation using standard metric specifications
- **Error Handling**: Automatic retry mechanisms for failed thread creation

## Motivation and Design Rationale
The project evolved from Fusion 360's built-in sample scripts through iterative development:

1. **Trial and Error Analysis**: Multiple test runs identified dimension limits and failure modes
2. **Industrial Standards**: Dimension ranges aligned with Standard Metric Bolt Dimensions from McMaster-Carr
3. **Data Curation**: Created 1000+ unique entries in Excel templates to ensure sufficient valid outputs
4. **Robustness**: Implemented fallback mechanisms for thread creation failures

## Requirements
- **Autodesk Fusion 360** (DESIGN workspace must be active)
- **Fusion Scripting Environment** (Python via Fusion's API)
- **CSV Data File** with bolt dimensions (see Data Format section)
- **Source Excel Templates**: `Shuffled_Expanded1.xlsx`, `Expanded1.xlsx`, `dset1.xlsx`

## Data Format
The script expects a CSV file with the following structure:

| Column | Name | Type | Description | Units |
|--------|------|------|-------------|-------|
| 1 | thread_size | string | Thread designation (e.g., M8) | - |
| 2 | body_diameter_mm | float | Bolt shank diameter | mm |
| 3 | pitch_mm | float | Thread pitch | mm |
| 4 | head_diameter_mm | float | Hex head diameter | mm |
| 5 | body_length_mm | float | Bolt length | mm |
| 6 | head_height_mm | float | Hex head height | mm |

### Example CSV Format
```csv
thread_size,body_diameter_mm,pitch_mm,head_diameter_mm,body_length_mm,head_height_mm
M8,8,1.25,13,40,5.5
M10,10,1.5,16,50,6.4
M12,12,1.75,18,60,7.5
```

**Important**: The script converts mm to cm internally for Fusion 360 geometry operations.

## Installation
1. Open Fusion 360
2. Navigate to **Utilities** → **Scripts and Add-ins**
3. Create a new Python script or open an existing one
4. Copy and paste the contents of `test.py`
5. Save the script

## Usage

### Step 1: Prepare Your Data
1. Use the provided Excel templates (`Shuffled_Expanded1.xlsx`, `Expanded1.xlsx`, `dset1.xlsx`) as reference
2. Export your bolt dimension data to CSV format
3. Ensure the CSV follows the format specified above

### Step 2: Run the Script
1. Ensure the **DESIGN workspace** is active in Fusion 360
2. Run your saved script from **Scripts and Add-ins**
3. The script will display a configuration dialog

### Step 3: Configure Parameters
- **CSV File Path**: Full path to your CSV file
- **Export Directory**: Directory for STL files (defaults to `~/Desktop/stl_files`)
- **Tracking File**: JSON file for progress tracking (defaults to `<Export Directory>/bolt_tracking.json`)
- **Spacing**: Not used for layout (bolts are exported and deleted immediately)

### Step 4: Generate Bolts
1. Click **"Create Next Batch of Bolts"**
2. The script generates up to 250 STL files per run
3. Progress is displayed in a dialog with cancel option
4. Repeat until all 1000 bolts are generated

### Batch Progress
- **Run 1**: Bolts 1-250
- **Run 2**: Bolts 251-500  
- **Run 3**: Bolts 501-750
- **Run 4**: Bolts 751-1000

## Output Structure

### Generated Files
- **STL Files**: `bolt_<N>.stl` (N = 1 to 1000)
- **Tracking File**: `bolt_tracking.json`

### Tracking File Format
```json
{
  "last_bolt": 250,
  "used_indices": [0, 1, 2, ..., 249]
}
```

## Technical Implementation

### Bolt Generation Process
1. **Hex Head Creation**: Sketched hexagon, extruded to specified height
2. **Body Generation**: Cylindrical body with chamfered end
3. **Feature Addition**: Fillets on head edges, revolve cuts for head shaping
4. **Threading**: Standard metric thread creation with fallback mechanisms
5. **Export**: STL export with medium mesh refinement
6. **Cleanup**: Component deletion to manage memory

### Thread Creation Strategy
- Uses standard metric sizes: 1, 1.6, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 42, 45, 48
- Coarse pitch mapping for each size
- Automatic retry with smaller sizes if thread creation fails
- Fallback to simplified thread designation if needed

### Error Handling
- **Thread Failures**: Automatic retry with alternative parameters
- **Invalid Geometries**: Bolt discarded, new attempt with different dimensions
- **Progress Persistence**: JSON tracking ensures resume capability after crashes

## Data Sources and Standards

### Industrial References
- **McMaster-Carr Metric Standards**: [Metric Hex Head Screws](https://www.mcmaster.com/screws/hex-head-screws/system-of-measurement~metric/)
- **Standard Metric Bolt Dimensions**: Industry-standard size and pitch specifications

### Dataset Curation
- **Range Validation**: Tested dimension limits through iterative generation
- **Uniqueness**: 1000+ entries ensure sufficient variety despite invalid combinations
- **Quality Control**: Excel templates maintain consistency and traceability

## Verification and Quality Control

### Verification Script
Use `verify_bolts.py` (available in the Git repository) to:
- Validate STL file presence and numbering
- Check consistency with tracking data
- Identify missing or corrupted files

### Quality Metrics
- **Mesh Quality**: Medium refinement for balance of detail and file size
- **Geometric Accuracy**: Standard metric thread specifications
- **Uniqueness**: Each bolt has distinct dimensional parameters

## Troubleshooting

### Common Issues

#### CSV Loading Errors
- **Problem**: "No valid data was loaded from the CSV file"
- **Solution**: Check file path and ensure CSV has exactly 6 columns with proper data types

#### All Dimensions Used
- **Problem**: "All bolt dimensions have been used"
- **Solution**: Expand your dataset with more unique dimension combinations

#### Fusion 360 Hangs
- **Problem**: Application becomes unresponsive
- **Solution**: 
  - Stick to 250 bolts per run
  - Close other applications
  - Use local export directory (not network paths)

#### Thread Creation Failures
- **Problem**: Frequent thread generation failures
- **Solution**: 
  - Ensure body diameters align with standard metric sizes
  - Review CSV dimension ranges
  - Check for unrealistic parameter combinations

### Performance Optimization
- **Batch Size**: Fixed at 250 to prevent memory issues
- **Memory Management**: Components deleted after export
- **Progress Tracking**: Resume capability reduces wasted computation

## Future Work

### Planned Enhancements
- **ML Model Training**: PointNet and PointNeXt implementation on generated dataset
- **Parameter Optimization**: Reduce thread creation failures through better dimension mapping
- **Extended Families**: Support for socket head, countersunk, and other fastener types
- **Material Properties**: Integration with material databases and properties

### Research Applications
- **Computer Vision**: Training data for bolt recognition and classification
- **Manufacturing**: Quality control and inspection systems
- **Design Automation**: Parameter optimization for custom fastener design

## Project Structure
```
mech sop/
├── test.py                          # Main Fusion 360 script
├── README.md                        # This file
├── dset1.xlsx                      # Original dataset template
├── Expanded1.xlsx                  # Expanded dataset
├── Shuffled_Expanded1.xlsx         # Shuffled dataset for generation
├── Archive/                        # Generated STL files
│   ├── bolt_1.stl
│   ├── bolt_2.stl
│   └── ... (1000+ STL files)
├── prev-sem-report.pdf             # Previous semester report
├── final-report.pdf                # Final project report
└── bolt_tracking.json              # Progress tracking (generated)
```

## Credits
- **Base Implementation**: Adapted from Fusion 360's built-in sample scripting patterns
- **Custom Development**: Extended with data loading, range curation, threading robustness, and batch export functionality
- **Industrial Standards**: Dimension ranges based on McMaster-Carr metric specifications

## License
MIT Licence

## Contributing
This project demonstrates automated 3D dataset generation for mechanical components. Contributions are welcome for:
- Enhanced error handling
- Additional fastener types
- ML model integration
- Performance optimization

## Support
For issues related to:
- **Fusion 360 Scripting**: Check Autodesk's official documentation
- **Dataset Generation**: Review the Excel templates and CSV format requirements
- **Thread Creation**: Ensure dimensions align with standard metric specifications

---

**Last Updated**: 2/9/25
**Fusion 360 Version**: Tested with recent versions
**Python Version**: As required by Fusion 360's scripting environment 
