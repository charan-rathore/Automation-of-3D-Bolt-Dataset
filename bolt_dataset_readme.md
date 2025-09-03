# 🔩 3D Bolt Dataset Generator for Fusion 360

Generate large-scale, labeled 3D datasets of metric hex-head bolts directly from Autodesk Fusion 360 with full automation. This project streamlines the entire pipeline from parametric CAD modeling to dataset curation and STL export, perfect for machine learning and industrial applications.

[![Python](https://img.shields.io/badge/Python-Fusion%20360%20API-blue.svg)](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](#)

## ⚡ Overview

Automate the creation of realistic, threaded 3D bolt geometries at scale — perfect for training 3D ML models like PointNet/PointNeXt, computer vision systems, quality inspection applications, or design automation workflows.

**Key Highlights:**
- 🛠 **Batch Generation**: 250 bolts per run optimized for Fusion 360 stability
- 📊 **Crash-Safe**: JSON-based progress tracking with automatic resume capability
- 🔑 **Unique Geometries**: Ensures no duplicate bolt configurations
- 🌀 **Realistic Threads**: Metric-compliant thread generation with intelligent fallback
- 📦 **Optimized Export**: Medium refinement STL meshes balancing detail and file size
- 🛡 **Robust Error Handling**: Automatic retries and comprehensive geometry validation

## 🎯 Motivation

Born from extensive experimentation with Fusion 360's scripting environment, this project addresses the critical need for high-quality 3D training data in manufacturing and computer vision applications. Through iterative development, we've created a robust pipeline that handles the complexities of parametric CAD automation.

### Why This Matters
- **Machine Learning**: High-quality 3D datasets are scarce and expensive
- **Industrial Standards**: Geometries mapped to real-world McMaster-Carr specifications  
- **Scalability**: Generate thousands of unique, labeled samples automatically
- **Research**: Enable advanced 3D point cloud and mesh-based ML research

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Automated Pipeline** | Complete workflow from CSV parameters to STL files |
| 📐 **Metric Compliance** | Standard M1-M48 thread sizes with proper pitch mapping |
| 🔄 **Progress Tracking** | Resume interrupted runs without data loss |
| 🎲 **Parameter Variation** | Intelligent sampling across dimensional space |
| 🔧 **Quality Assurance** | Built-in verification and validation scripts |
| ⚡ **Performance Optimized** | Memory management and batch processing for stability |

## 📋 Requirements

- **Autodesk Fusion 360** (DESIGN workspace active)
- **Fusion 360 Python API** environment
- **CSV dataset file** with bolt parameters (templates provided)

### Supported Formats
- Excel templates: `dset1.xlsx`, `Expanded1.xlsx`, `Shuffled_Expanded1.xlsx`
- CSV export from Excel with proper schema

## 📊 Data Schema

Your CSV file should follow this exact format:

| Column | Name | Type | Description | Units |
|--------|------|------|-------------|-------|
| 1 | `thread_size` | string | Thread designation (e.g., M8) | - |
| 2 | `body_diameter_mm` | float | Shank diameter | mm |
| 3 | `pitch_mm` | float | Thread pitch | mm |
| 4 | `head_diameter_mm` | float | Hex head diameter | mm |
| 5 | `body_length_mm` | float | Bolt length | mm |
| 6 | `head_height_mm` | float | Hex head height | mm |

### Example Data
```csv
thread_size,body_diameter_mm,pitch_mm,head_diameter_mm,body_length_mm,head_height_mm
M8,8,1.25,13,40,5.5
M10,10,1.5,16,50,6.4
M12,12,1.75,18,60,7.5
```

> ⚠️ **Note**: Units are automatically converted from mm → cm internally for Fusion 360 operations.

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/3d-bolt-dataset-generator.git
cd 3d-bolt-dataset-generator
```

1. Open **Autodesk Fusion 360**
2. Navigate to **Utilities → Scripts and Add-ins**
3. Create a new Python script or open existing
4. Copy-paste `test.py` content and save

### 2. Prepare Your Data
```bash
# Export your Excel template to CSV format
# Ensure column headers match the schema above
```

### 3. Run Generation
1. **Launch script** in Fusion 360 (DESIGN workspace must be active)
2. **Configure dialog** with:
   - CSV file path
   - Export directory (default: `~/Desktop/stl_files`)
   - Tracking file (`bolt_tracking.json`)
3. **Start generation** - creates 250 STL files per batch

### 4. Monitor Progress
```json
// bolt_tracking.json
{
  "last_bolt": 250,
  "used_indices": [0, 1, 2, ..., 249],
  "timestamp": "2025-09-03T10:30:00Z"
}
```

## 📈 Typical Workflow

| Run | Bolts Generated | Progress |
|-----|-----------------|----------|
| Run 1 | 1-250 | 25% |
| Run 2 | 251-500 | 50% |
| Run 3 | 501-750 | 75% |
| Run 4 | 751-1000 | 100% |

## 🛠 Technical Architecture

### Generation Pipeline
```
CSV Data → Parameter Validation → Hex Head Creation → Cylindrical Body → 
Thread Generation → Feature Addition → STL Export → Component Cleanup
```

### Thread Strategy
- **Primary**: Standard metric sizes (M1 → M48)
- **Fallback**: Reduced pitch for threading failures  
- **Final**: Simplified thread geometry if all else fails
- **Quality Control**: Automatic geometry validation

### Error Handling
- **Thread Failures**: Multi-level retry with parameter adjustment
- **Invalid Geometry**: Skip and regenerate with logging
- **Crash Recovery**: JSON-based state restoration
- **Memory Management**: Component cleanup after each bolt

## 📂 Project Structure

```
mech-sop/
├── 📜 test.py                    # Main Fusion 360 script
├── 📖 README.md                  # This documentation
├── 📊 dset1.xlsx                 # Base dataset template
├── 📊 Expanded1.xlsx             # Extended dataset
├── 📊 Shuffled_Expanded1.xlsx    # Randomized dataset
├── 🗂 Archive/                   # Generated STL files
│   ├── bolt_1.stl
│   ├── bolt_2.stl
│   └── ... (1000+ files)
├── 📋 bolt_tracking.json         # Progress tracking
├── 🐍 verify_bolts.py           # Quality verification script
└── 📄 *.pdf                     # Documentation reports
```

## 🔍 Quality Verification

Run the verification script to check dataset integrity:

```python
python verify_bolts.py
```

**Verification Checks:**
- ✅ File presence and sequential numbering
- ✅ Tracking file consistency  
- ✅ STL file corruption detection
- ✅ Geometry validation metrics

## 🎯 Applications

| Domain | Use Case |
|--------|----------|
| 🤖 **Machine Learning** | 3D point cloud classification, object detection |
| 🏭 **Manufacturing** | Quality control automation, defect detection |
| 🖥 **Computer Vision** | Bolt recognition, pose estimation |
| ⚙️ **CAD Automation** | Parametric design optimization |
| 🔬 **Research** | 3D geometry analysis, mesh processing |

## 🔮 Future Roadmap

- [ ] **Enhanced ML Integration**: Direct PointNet/PointNeXt training pipelines
- [ ] **Extended Fastener Family**: Socket head, countersunk, and custom bolts  
- [ ] **Material Properties**: PBR textures and material assignments
- [ ] **Advanced Threading**: More robust thread generation algorithms
- [ ] **Cloud Integration**: Distributed generation across multiple Fusion instances
- [ ] **Dataset Augmentation**: Automated noise, wear, and damage simulation

## 🤝 Contributing

We welcome contributions! Here are some areas where you can help:

- 🔧 **Threading Logic**: Improve robustness for edge cases
- 🆕 **Fastener Types**: Add support for new bolt/screw families  
- 🧠 **ML Pipelines**: Integration with popular ML frameworks
- ⚡ **Performance**: Optimization for larger batch sizes
- 📚 **Documentation**: Tutorials and advanced usage guides

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test with Fusion 360
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Autodesk Fusion 360**: For comprehensive API and scripting environment
- **McMaster-Carr**: For metric bolt specifications and standards
- **Community**: For testing, feedback, and contributions

## 📞 Support

- 📖 **Fusion 360 Scripting**: [Official Autodesk Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- 🐛 **Issues**: Use GitHub Issues for bug reports and feature requests
- 💬 **Discussions**: Join our community discussions for questions and tips

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/3d-bolt-dataset-generator?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/3d-bolt-dataset-generator?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/3d-bolt-dataset-generator)

---

<p align="center">
  <b>⭐ Star this repository if you find it useful! ⭐</b><br>
  <sub>Last Updated: September 2025 | Tested on: Fusion 360 Latest Versions</sub>
</p>