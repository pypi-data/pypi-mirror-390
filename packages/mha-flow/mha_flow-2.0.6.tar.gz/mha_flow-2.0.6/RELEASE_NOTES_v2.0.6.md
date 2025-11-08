# MHA-Flow v2.0.6 Release Notes

**Release Date:** November 8, 2025  
**Version:** 2.0.6  
**Previous Version:** 2.0.5

## 🎯 Overview

Version 2.0.6 is a major quality-of-life update that significantly improves the web interface, history tracking, and results persistence in the MHA Toolbox.

## ✨ New Features

### 1. **Unique Run IDs for History Entries**
- Every optimization run now gets a unique UUID identifier
- Prevents results from being overwritten
- Allows precise tracking and retrieval of specific runs
- Implemented in `save_to_user_history()` function

### 2. **Comprehensive Dataset Metadata Storage**
- History now saves complete dataset information:
  - Dataset name
  - Number of samples (n_samples)
  - Number of features (n_features)  
  - Number of classes (n_classes)
  - Target names
  - Feature names
- Enhanced History page displays all metadata
- Better understanding of past experiments

### 3. **Persistent Results File Storage**
- New `save_results_to_file()` function
- Results automatically saved to JSON files in user's directory
- Structure: `persistent_state/results/{username}/{timestamp}_{run_id}.json`
- Can reload complete results from History page using "Load Full Results" button
- New `load_results_from_file()` function for retrieval

### 4. **Running Animation with Hourglass Emoji**
- Added ⏳ hourglass emoji to running status
- Pulsing CSS animation applied
- Shows "Running..." and "Queued..." states
- Visual feedback improves user experience
- Located at lines 2574 and 2583 in `mha_ui_complete.py`

### 5. **Fixed Algorithm Count Display**
- Removed hardcoded algorithm groups (only showed ~50 algorithms)
- Now dynamically loads from `ALGORITHM_CATEGORIES`
- Displays all 137 algorithms (105 main + 32 hybrid):
  - Evolutionary Algorithms
  - Swarm Intelligence
  - Bio-Inspired Algorithms
  - Physics-Based Algorithms
  - Human-Based Algorithms
  - Hybrid Algorithms
  - Advanced Meta-Heuristics
  - Search-Based Algorithms
  - Nature-Inspired Algorithms
  - Mathematical Algorithms
  - Game-Based Algorithms
  - Pandemic-Inspired Algorithms

### 6. **Duplicate Header Removal**
- Removed "MHA Toolbox" headers from:
  - Disclaimer page (line 1146)
  - Authentication page (line 1266)
- Kept only one header on the main home page
- Cleaner, more professional UI

## 🔧 Technical Improvements

### Code Changes

**File: `mha_ui_complete.py`**

1. **Enhanced `save_to_user_history()` function (lines 1081-1168)**:
   ```python
   - Added UUID generation: run_id = str(uuid.uuid4())
   - Added comprehensive dataset_info dictionary
   - Stores dataset shape, class count, feature names
   - Calls save_results_to_file() for persistence
   ```

2. **New `save_results_to_file()` function (lines 1171-1205)**:
   ```python
   - Creates user-specific results directory
   - Generates timestamped JSON files
   - Stores complete metadata + results
   - Returns filepath for verification
   ```

3. **New `load_results_from_file()` function (lines 1208-1234)**:
   ```python
   - Searches for results by run_id
   - Returns complete data dictionary
   - Handles file not found gracefully
   ```

4. **Updated History page (lines 4471-4514)**:
   ```python
   - Displays all dataset metadata
   - Shows samples, features, classes
   - "Load Full Results" button added
   - Better formatted algorithm lists
   ```

5. **Algorithm categories (lines 2375-2387)**:
   ```python
   - Removed hardcoded groups
   - Dynamically loads from ALGORITHM_CATEGORIES
   - Supports all 137 algorithms
   - Removes emoji prefixes for clean display
   ```

6. **Running animation (lines 2574, 2583)**:
   ```python
   - Added ⏳ emoji
   - Applied pulsing CSS class
   - Shows algorithm progress clearly
   ```

**File: `mha_toolbox/__init__.py`**
- Updated version to `2.0.6`

**File: `setup.py`**
- Updated version comment to `v2.0.6`
- Updated fallback version

## 📊 Algorithm Discovery Stats

The system successfully discovers and registers:
- **137 Total Algorithms**
  - 105 Main Algorithms
  - 32 Hybrid Algorithms
- **298 Algorithm Aliases** for easy access

## 🐛 Bug Fixes

1. **History Overwriting Issue**: Fixed by adding unique run IDs
2. **Dataset Information Loss**: Now saves complete metadata
3. **Results Not Persistent**: Implemented file-based storage
4. **Missing Visual Feedback**: Added running animation
5. **Incomplete Algorithm List**: Now shows all 137 algorithms

## 📝 Files Modified

1. `mha_ui_complete.py` - Major updates
2. `mha_toolbox/__init__.py` - Version bump
3. `setup.py` - Version update

## 🚀 Installation

```bash
# Upgrade from PyPI
pip install --upgrade mha-flow

# Or install specific version
pip install mha-flow==2.0.6
```

## 💡 Usage Examples

### Accessing History with New Features

```python
# Run mha-demo
mha-demo

# In the web interface:
# 1. Navigate to "📜 History" page
# 2. See detailed dataset metadata
# 3. Click "Load Full Results" to reload any past run
# 4. Filter by dataset, task type, or sort by metrics
```

### Running Optimization

```python
# All 137 algorithms available for selection
# Visual feedback with hourglass animation
# Results automatically saved with unique ID
# Complete dataset metadata tracked
```

## 🔍 System Integrity

- ✅ All 137 algorithms properly registered
- ✅ Dynamic category system working
- ✅ File persistence functional  
- ✅ History tracking enhanced
- ✅ UI improvements applied
- ✅ No breaking changes

## 📚 Documentation

- Installation guide: `INSTALLATION_USAGE_GUIDE.md`
- README: `README.md`
- License: `LICENSE`

## 🙏 Credits

**Developed by:** Achyut103040  
**Repository:** https://github.com/Achyut103040/MHA-Algorithm  
**PyPI Package:** https://pypi.org/project/mha-flow/

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/Achyut103040/MHA-Algorithm/issues
- PyPI: https://pypi.org/project/mha-flow/

---

**Happy Optimizing! 🚀**
