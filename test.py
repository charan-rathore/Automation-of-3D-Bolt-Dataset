import adsk.core, adsk.fusion, traceback
import math
import random
import os
import json

# Global variables
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

# Class to store bolt dimensions from CSV
class BoltDimensions:
    def __init__(self):
        self.thread_sizes = []
        self.body_diameters = []
        self.pitches = []
        self.head_diameters = []
        self.body_lengths = []
        self.head_heights = []
        self.used_indices = set()  # Keep track of used bolt indices
        self.is_loaded = False     # Flag to track if data is loaded
        
    def load_from_csv(self, file_path):
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                if ui:
                    ui.messageBox(f'CSV file not found: {file_path}')
                return False
                
            # Clear existing data if any
            self.thread_sizes = []
            self.body_diameters = []
            self.pitches = []
            self.head_diameters = []
            self.body_lengths = []
            self.head_heights = []
            # Do not clear used_indices here as we want to maintain that across CSV reloads
                
            # Open and read the CSV file
            with open(file_path, 'r') as file:
                # Skip header row
                header = file.readline()
                
                # Read data rows
                line_count = 0
                for line in file:
                    # Skip empty lines
                    if not line.strip():
                        continue
                        
                    # Parse CSV row (handle commas within fields)
                    values = self._parse_csv_line(line)
                    
                    if len(values) >= 6:  # Ensure we have enough values
                        try:
                            self.thread_sizes.append(values[0])
                            self.body_diameters.append(float(values[1]))
                            self.pitches.append(float(values[2]))
                            self.head_diameters.append(float(values[3]))
                            self.body_lengths.append(float(values[4]))
                            self.head_heights.append(float(values[5]))
                            line_count += 1
                        except ValueError as e:
                            if ui:
                                ui.messageBox(f'Error parsing line: {line}\nError: {str(e)}')
                            continue
            
            self.is_loaded = line_count > 0
            
            if self.is_loaded:
                if ui:
                    ui.messageBox(f'Successfully loaded {line_count} bolt dimensions from CSV.')
                return True
            else:
                if ui:
                    ui.messageBox('No valid data was loaded from the CSV file.')
                return False
            
        except Exception as e:
            if ui:
                ui.messageBox(f'Error reading CSV file:\n{str(e)}')
            return False
    
    def _parse_csv_line(self, line):
        """Simple CSV parser that handles basic CSV format"""
        result = []
        in_quotes = False
        current = ''
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                result.append(current.strip())
                current = ''
            else:
                current += char
                
        # Add the last field
        if current:
            result.append(current.strip())
            
        return result
    
    def set_used_indices(self, indices):
        """Set the used indices from an external source"""
        self.used_indices = set(indices)
    
    def get_unused_indices(self):
        """Get a list of all unused indices"""
        if not self.is_loaded or len(self.body_diameters) == 0:
            return []
        
        return list(set(range(len(self.body_diameters))) - self.used_indices)
    
    def get_random_unused_bolt(self):
        """Get a random unused bolt index"""
        if not self.is_loaded or len(self.body_diameters) == 0:
            raise ValueError("No bolt dimensions loaded. Please load the CSV file first.")
            
        available_indices = list(set(range(len(self.body_diameters))) - self.used_indices)
        
        if not available_indices:
            # All indices used, handle this situation
            if ui:
                ui.messageBox('All bolt dimensions have been used. No more unique bolts can be created.')
            raise ValueError("No available bolt indices found. All indices have been used.")
            
        index = random.choice(available_indices)
        self.used_indices.add(index)
        return index

# Global bolt dimensions instance
bolt_dimensions = BoltDimensions()

# Function to ensure the export directory exists
def ensure_export_directory(dir_path):
    """Create the export directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            return True
        except Exception as e:
            if ui:
                ui.messageBox(f'Failed to create directory: {dir_path}\nError: {str(e)}')
            return False
    return True

# Function to export a component as STL
def export_as_stl(component, file_path):
    """Export a component as an STL file"""
    try:
        # Get the active product
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        # Export the component using the design's exportManager
        exportMgr = design.exportManager
        
        # Create STL export options
        stlOptions = exportMgr.createSTLExportOptions(component)
        stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
        stlOptions.filename = file_path
        
        # Execute the export
        exportMgr.execute(stlOptions)
        return True
    except Exception as e:
        if ui:
            ui.messageBox(f'Failed to export STL: {file_path}\nError: {str(e)}')
        return False

# JSON tracking functions
def load_tracking_data(file_path):
    """Load tracking data from JSON file"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            if ui:
                ui.messageBox(f'Error loading tracking file: {str(e)}')
            return {"last_bolt": 0, "used_indices": []}
    else:
        # If file doesn't exist, create a new one with default values
        return {"last_bolt": 0, "used_indices": []}

def save_tracking_data(file_path, data):
    """Save tracking data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        if ui:
            ui.messageBox(f'Error saving tracking file: {str(e)}')
        return False

# Main class for bolt creation
class Bolt:
    def __init__(self, position_x=0, position_y=0):
        try:
            # Get a random unused bolt index from our dataset
            self.index = bolt_dimensions.get_random_unused_bolt()
            
            # Get parameters from the CSV data based on the selected index
            self._boltName = f'Bolt_{random.randint(1000, 9999)}'
            self._headDiameter = bolt_dimensions.head_diameters[self.index] / 10  # cm
            self._bodyDiameter = bolt_dimensions.body_diameters[self.index] / 10  # cm
            self._headHeight = bolt_dimensions.head_heights[self.index] / 10  # cm
            
            # Store the raw value for bodyLength
            self._bodyLengthValue = bolt_dimensions.body_lengths[self.index] / 10  # cm
            
            # These values are derived from body diameter with some random variation as in original
            self._cutAngle = (30.0 + random.uniform(-5, 5)) * (math.pi / 180)  # radians
            self._chamferDistanceValue = (self._bodyDiameter * 0.0769) + random.uniform(-0.01, 0.01)
            self._filletRadiusValue = (self._bodyDiameter * 0.05988) + random.uniform(-0.01, 0.01)
            
            # Position for placement in grid
            self.position_x = position_x
            self.position_y = position_y
            
            # Store thread specifications - Use standard sizes
            self.threadType = random.choice(['ANSI Metric M Profile', 'GB Metric profile', 'ISO Metric profile'])  
            
            # Extract the numeric part for the thread designation
            # Round to standard metric bolt sizes to avoid thread creation errors
            self.std_sizes = [1, 1.6, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 42, 45, 48]
            dia = bolt_dimensions.body_diameters[self.index]
            
            # Find the closest standard size
            self.closest_size = min(self.std_sizes, key=lambda x: abs(x - dia))
            
            # Standard pitches for standard sizes (coarse thread)
            self.pitch_map = {
                1: 0.25, 1.6: 0.35, 2: 0.4, 2.5: 0.45, 3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0,
                8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 18: 2.5, 20: 2.5,
                22: 2.5, 24: 3.0, 27: 3.0, 30: 3.5, 33: 3.5, 36: 4.0, 39: 4.0, 42: 4.5, 45: 4.5, 48: 5.0
            }
            
            self.std_pitch = self.pitch_map.get(self.closest_size, 1.5)  # Default to 1.5 if size not found
            
            # Use standard thread designation
            self.threadDesignation = f'M{self.closest_size}x{self.std_pitch}'
            self.threadClass = '6g'
            
            # Flag to track if thread creation was successful
            self.thread_created = False
            
        except Exception as e:
            if ui:
                ui.messageBox(f'Error initializing bolt: {str(e)}')
            raise

    # Properties
    @property
    def boltName(self):
        return self._boltName
    @boltName.setter
    def boltName(self, value):
        self._boltName = value

    @property
    def headDiameter(self):
        return self._headDiameter
    @headDiameter.setter
    def headDiameter(self, value):
        self._headDiameter = value

    @property
    def bodyDiameter(self):
        return self._bodyDiameter
    @bodyDiameter.setter
    def bodyDiameter(self, value):
        self._bodyDiameter = value 

    @property
    def headHeight(self):
        return self._headHeight
    @headHeight.setter
    def headHeight(self, value):
        self._headHeight = value 

    @property
    def bodyLengthValue(self):
        return self._bodyLengthValue
    @bodyLengthValue.setter
    def bodyLengthValue(self, value):
        self._bodyLengthValue = value   

    @property
    def cutAngle(self):
        return self._cutAngle
    @cutAngle.setter
    def cutAngle(self, value):
        self._cutAngle = value  

    @property
    def chamferDistanceValue(self):
        return self._chamferDistanceValue
    @chamferDistanceValue.setter
    def chamferDistanceValue(self, value):
        self._chamferDistanceValue = value

    @property
    def filletRadiusValue(self):
        return self._filletRadiusValue
    @filletRadiusValue.setter
    def filletRadiusValue(self, value):
        self._filletRadiusValue = value

    def createThreads(self, newComp, sideFace):
        """Create threads with proper error handling and retry mechanism"""
        try:
            threads = newComp.features.threadFeatures
            isInternal = False
            
            # Try with the current thread designation
            threadInfo = threads.createThreadInfo(isInternal, self.threadType, self.threadDesignation, self.threadClass)
            faces = adsk.core.ObjectCollection.create()
            faces.add(sideFace)
            threadInput = threads.createInput(faces, threadInfo)
            threadInput.isModeled = True
            threads.add(threadInput)
            self.thread_created = True
            return True
        except Exception as e:
            # First attempt failed, try with different thread parameters
            try:
                # Try with the next smaller size if current size is too large
                available_sizes = [size for size in self.std_sizes if size < self.closest_size]
                if available_sizes:
                    new_size = max(available_sizes)
                    new_pitch = self.pitch_map.get(new_size, 1.0)
                    new_designation = f'M{new_size}x{new_pitch}'
                    
                    threadInfo = threads.createThreadInfo(isInternal, self.threadType, new_designation, self.threadClass)
                    faces = adsk.core.ObjectCollection.create()
                    faces.add(sideFace)
                    threadInput = threads.createInput(faces, threadInfo)
                    threadInput.isModeled = True
                    threads.add(threadInput)
                    self.thread_created = True
                    return True
                else:
                    # Try with a simpler thread designation
                    basic_designation = f'M{self.closest_size}'
                    threadInfo = threads.createThreadInfo(isInternal, self.threadType, basic_designation, self.threadClass)
                    faces = adsk.core.ObjectCollection.create()
                    faces.add(sideFace)
                    threadInput = threads.createInput(faces, threadInfo)
                    threadInput.isModeled = True
                    threads.add(threadInput)
                    self.thread_created = True
                    return True
            except Exception as e:
                return False
        
        return False

    def buildBolt(self, rootComp):
        try:
            # Create a new component
            allOccs = rootComp.occurrences
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(self.position_x, self.position_y, 0)
            newOcc = allOccs.addNewComponent(transform)
            newComp = newOcc.component
            
            if newComp is None:
                ui.messageBox('New component failed to create', 'New Component Failed')
                return None

            # Create a new sketch for the hex head
            sketches = newComp.sketches
            xyPlane = newComp.xYConstructionPlane
            xzPlane = newComp.xZConstructionPlane
            sketch = sketches.add(xyPlane)
            center = adsk.core.Point3D.create(0, 0, 0)
            vertices = []
            for i in range(0, 6):
                vertex = adsk.core.Point3D.create(center.x + (self.headDiameter/2) * math.cos(math.pi * i / 3), 
                                               center.y + (self.headDiameter/2) * math.sin(math.pi * i / 3), 0)
                vertices.append(vertex)

            for i in range(0, 6):
                sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])

            # Extrude the head
            extrudes = newComp.features.extrudeFeatures
            prof = sketch.profiles[0]
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance = adsk.core.ValueInput.createByReal(self.headHeight)
            extInput.setDistanceExtent(False, distance)
            headExt = extrudes.add(extInput)

            # Name the body
            fc = headExt.faces[0]
            bd = fc.body
            bd.name = self.boltName

            # Create the bolt body
            bodySketch = sketches.add(xyPlane)
            bodySketch.sketchCurves.sketchCircles.addByCenterRadius(center, self.bodyDiameter/2)
            bodyProf = bodySketch.profiles[0]
            bodyExtInput = extrudes.createInput(bodyProf, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            bodyExtInput.setAllExtent(adsk.fusion.ExtentDirections.NegativeExtentDirection)
            
            # Create ValueInput objects from raw values at the point of use
            bodyLength_value = adsk.core.ValueInput.createByReal(self.bodyLengthValue)
            bodyExtInput.setDistanceExtent(False, bodyLength_value)
            bodyExt = extrudes.add(bodyExtInput)

            # Create chamfer
            edgeCol = adsk.core.ObjectCollection.create()
            edges = bodyExt.endFaces[0].edges
            for edgeI in edges:
                edgeCol.add(edgeI)

            chamferFeats = newComp.features.chamferFeatures
            chamferInput = chamferFeats.createInput(edgeCol, True)
            
            # Create ValueInput from raw value
            chamferDistance_value = adsk.core.ValueInput.createByReal(self.chamferDistanceValue)
            chamferInput.setToEqualDistance(chamferDistance_value)
            chamferFeats.add(chamferInput)

            # Create fillet
            edgeCol.clear()
            loops = headExt.endFaces[0].loops
            edgeLoop = None
            for loop in loops:
                # Find the loop with one edge (the circular edge)
                if len(loop.edges) == 1:
                    edgeLoop = loop
                    break

            edgeCol.add(edgeLoop.edges[0])  
            filletFeats = newComp.features.filletFeatures
            filletInput = filletFeats.createInput()
            
            # Create ValueInput from raw value
            filletRadius_value = adsk.core.ValueInput.createByReal(self.filletRadiusValue)
            filletInput.addConstantRadiusEdgeSet(edgeCol, filletRadius_value, True)
            filletFeats.add(filletInput)

            # Create revolve feature 1 (bottom cut)
            revolveSketchOne = sketches.add(xzPlane)
            radius = self.headDiameter/2
            point1 = revolveSketchOne.modelToSketchSpace(adsk.core.Point3D.create(center.x + radius*math.cos(math.pi/6), 0, center.y))
            point2 = revolveSketchOne.modelToSketchSpace(adsk.core.Point3D.create(center.x + radius, 0, center.y))
            point3 = revolveSketchOne.modelToSketchSpace(adsk.core.Point3D.create(point2.x, 0, (point2.x - point1.x) * math.tan(self.cutAngle)))
            revolveSketchOne.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            revolveSketchOne.sketchCurves.sketchLines.addByTwoPoints(point2, point3)
            revolveSketchOne.sketchCurves.sketchLines.addByTwoPoints(point3, point1)

            # Create revolve feature 2 (top cut)
            revolveSketchTwo = sketches.add(xzPlane)
            point4 = revolveSketchTwo.modelToSketchSpace(adsk.core.Point3D.create(center.x + radius*math.cos(math.pi/6), 0, self.headHeight - center.y))
            point5 = revolveSketchTwo.modelToSketchSpace(adsk.core.Point3D.create(center.x + radius, 0, self.headHeight - center.y))
            point6 = revolveSketchTwo.modelToSketchSpace(adsk.core.Point3D.create(center.x + point2.x, 0, self.headHeight - center.y - (point5.x - point4.x) * math.tan(self.cutAngle)))
            revolveSketchTwo.sketchCurves.sketchLines.addByTwoPoints(point4, point5)
            revolveSketchTwo.sketchCurves.sketchLines.addByTwoPoints(point5, point6)
            revolveSketchTwo.sketchCurves.sketchLines.addByTwoPoints(point6, point4)

            # Revolve cuts
            zaxis = newComp.zConstructionAxis
            revolves = newComp.features.revolveFeatures
            revProf1 = revolveSketchTwo.profiles[0]
            revInput1 = revolves.createInput(revProf1, zaxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
            revAngle = adsk.core.ValueInput.createByReal(math.pi*2)
            revInput1.setAngleExtent(False, revAngle)
            revolves.add(revInput1)

            revProf2 = revolveSketchOne.profiles[0]
            revInput2 = revolves.createInput(revProf2, zaxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
            revInput2.setAngleExtent(False, revAngle)
            revolves.add(revInput2)
            
            # Create threads with improved error handling
            sideFace = bodyExt.sideFaces[0]
            thread_result = self.createThreads(newComp, sideFace)
            
            # If thread creation failed, return None to indicate this bolt should be discarded
            if not thread_result:
                # Delete the occurrence since we're discarding this bolt
                newOcc.deleteMe()
                return None
                
            return newComp

        except Exception as e:
            if ui:
                ui.messageBox(f'Failed to compute the bolt {self.boltName}:\n{str(e)}\n{traceback.format_exc()}')
            # If any error occurred, make sure to clean up the occurrence
            if 'newOcc' in locals() and newOcc is not None:
                try:
                    newOcc.deleteMe()
                except:
                    pass
            return None

# Main command handler
class BatchBoltCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs
            
            # Get input values
            boltCount = 250  # Fixed to 250 bolts per batch
            spacing = 5     # Default spacing in cm
            csv_path = ""   # CSV file path
            create_threads = True  # Flag to control thread creation
            export_dir = ""  # Export directory
            tracking_file = "" # JSON tracking file path
            
            for input in inputs:
                if input.id == 'spacing':
                    spacing = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'csvPath':
                    csv_path = input.value
                elif input.id == 'createThreads':
                    create_threads = input.value
                elif input.id == 'exportDir':
                    export_dir = input.value
                elif input.id == 'trackingFile':
                    tracking_file = input.value
            
            # Get default export directory if not specified
            if not export_dir:
                # Use desktop by default
                export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "stl_files")
            
            # Get default tracking file if not specified
            if not tracking_file:
                tracking_file = os.path.join(export_dir, "bolt_tracking.json")
            
            # Validate and create export directory
            if not ensure_export_directory(export_dir):
                ui.messageBox(f'Failed to create export directory: {export_dir}')
                args.isValidResult = False
                return
            
            # Validate and load CSV file
            if not csv_path:
                ui.messageBox('Please provide a valid CSV file path.')
                args.isValidResult = False
                return
                
            # Load tracking data
            tracking_data = load_tracking_data(tracking_file)
            last_bolt_num = tracking_data["last_bolt"]
            used_indices = tracking_data["used_indices"]
            
            # Calculate the current batch based on last_bolt_num
            current_batch = (last_bolt_num // 250) + 1
            if current_batch > 4:  # Already completed all 1000 bolts
                ui.messageBox('All 1000 bolts have already been generated. No further bolts will be created.')
                args.isValidResult = False
                return
                
            # Calculate how many bolts to create in this batch
            bolts_remaining = 1000 - last_bolt_num
            bolts_to_create = min(250, bolts_remaining)
            
            start_bolt_num = last_bolt_num + 1
            end_bolt_num = start_bolt_num + bolts_to_create - 1
            
            # Load bolt dimensions from CSV
            if not bolt_dimensions.load_from_csv(csv_path):
                ui.messageBox(f'Failed to load bolt dimensions from {csv_path}. Please check the file path and format.')
                args.isValidResult = False
                return
            
            # Make sure data was loaded successfully
            if not bolt_dimensions.is_loaded:
                ui.messageBox('No data was loaded from the CSV file.')
                args.isValidResult = False
                return
                
            # Set the used indices from tracking file
            bolt_dimensions.set_used_indices(used_indices)
            
            # Create bolts and export them
            result = self.createAndExportBolts(bolts_to_create, spacing, create_threads, export_dir, 
                                               start_bolt_num=start_bolt_num)
            
            if result:
                # Update tracking data with new information
                tracking_data["last_bolt"] = end_bolt_num
                tracking_data["used_indices"] = list(bolt_dimensions.used_indices)
                save_tracking_data(tracking_file, tracking_data)
                
                # Display information about the current batch and next batch
                next_batch = current_batch + 1
                if next_batch <= 4:
                    next_start = end_bolt_num + 1
                    next_end = next_start + 249
                    ui.messageBox(f'Completed batch {current_batch} (bolts {start_bolt_num}-{end_bolt_num}).\n\n'
                                 f'Next run will create batch {next_batch} (bolts {next_start}-{next_end}).')
                else:
                    ui.messageBox(f'Completed batch {current_batch} (bolts {start_bolt_num}-{end_bolt_num}).\n\n'
                                 f'All 1000 bolts have now been generated.')
                
            args.isValidResult = result

        except Exception as e:
            if ui:
                ui.messageBox(f'Failed:\n{str(e)}\n\n{traceback.format_exc()}')
            args.isValidResult = False

    def createAndExportBolts(self, count, spacing, create_threads=True, export_dir="", start_bolt_num=1):
        # Get the active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent
        
        # Create the specified number of bolts
        success_count = 0
        error_count = 0
        retry_count = 0
        export_count = 0
        
        # Continue creating bolts until we reach the requested count or hit max retries
        max_attempts = count * 3  # Allow up to 3x attempts to handle thread failures
        attempts = 0
        
        # Create a progress dialog
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.title = f'Creating and Exporting Bolts ({start_bolt_num} to {start_bolt_num + count - 1})'
        progressDialog.message = f'Processing bolt {start_bolt_num} of {start_bolt_num + count - 1}'
        progressDialog.minimumValue = 0
        progressDialog.maximumValue = count
        progressDialog.isCancelButtonShown = True
        
        try:
            while success_count < count and attempts < max_attempts:
                # Update progress dialog
                progressDialog.progressValue = success_count
                progressDialog.message = f'Processing bolt {start_bolt_num + success_count} of {start_bolt_num + count - 1}'
                adsk.doEvents()  # Process events to keep UI responsive
                
                # Check for cancel
                if progressDialog.wasCancelled:
                    break
                
                # Create a new bolt with unique parameters
                try:
                    # Create bolt at a dummy position since we're only exporting
                    bolt = Bolt(0, 0)
                    current_bolt_num = start_bolt_num + success_count
                    bolt.boltName = f'bolt_{current_bolt_num}'
                    component = bolt.buildBolt(rootComp)
                    
                    # Check if the bolt was successfully created with threads
                    if component is not None:
                        # Export as STL
                        stl_path = os.path.join(export_dir, f'bolt_{current_bolt_num}.stl')
                        if export_as_stl(component, stl_path):
                            export_count += 1
                            # Delete the component from the workspace after export
                            for occ in rootComp.occurrences:
                                if occ.component.name == component.name:
                                    occ.deleteMe()
                                    break
                        success_count += 1
                    else:
                        retry_count += 1
                except Exception as e:
                    error_count += 1
                    # Avoid showing message boxes during processing as they block the UI
                    # We'll report failures at the end
                
                attempts += 1
        finally:
            # Close progress dialog
            progressDialog.hide()
        
        message = f'Created and exported {export_count} bolts successfully to {export_dir}'
        if retry_count > 0:
            message += f' (discarded {retry_count} bolts that failed thread creation)'
        if error_count > 0:
            message += f' with {error_count} errors'
        
        ui.messageBox(message)
        
        # Return True if we successfully created at least one bolt
        return export_count > 0

class BatchBoltCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BatchBoltCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            
            # Add the command handlers
            onExecute = BatchBoltCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = BatchBoltCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = BatchBoltCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            
            # Keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            # Define the inputs
            inputs = cmd.commandInputs
            
            # Removed boltCount input since we fixed it at 250 per batch
            
            # Spacing between bolts (keep this for compatibility, though we don't display them)
            initSpacing = adsk.core.ValueInput.createByReal(5)
            inputs.addValueInput('spacing', 'Spacing Between Bolts', 'cm', initSpacing)
            
            # CSV file path input
            csvPathInput = inputs.addStringValueInput('csvPath', 'CSV File Path', '')
            csvPathInput.tooltip = 'Provide the full path to the CSV file containing bolt dimensions'
            
            # Add option to create threads
            createThreadsInput = inputs.addBoolValueInput('createThreads', 'Create Threads', True, '', True)
            createThreadsInput.tooltip = 'Enable/disable thread creation (disable if threads are causing errors)'
            
            # Export directory input with default to desktop
            defaultExportDir = os.path.join(os.path.expanduser("~"), "Desktop", "stl_files")
            exportDirInput = inputs.addStringValueInput('exportDir', 'Export Directory', defaultExportDir)
            exportDirInput.tooltip = 'Directory to export STL files (default is Desktop/stl_files)'
            
            # Tracking file input
            defaultTrackingFile = os.path.join(defaultExportDir, "bolt_tracking.json")
            trackingFileInput = inputs.addStringValueInput('trackingFile', 'Tracking File', defaultTrackingFile)
            trackingFileInput.tooltip = 'JSON file to track bolt creation progress across multiple runs'
            
            # Add informative text input
            infoInput = inputs.addTextBoxCommandInput('infoText', '', 
                'This script will create up to 250 bolts per run, tracking progress in a JSON file. ' + 
                'It will automatically continue from where the previous run left off until 1000 unique bolts are created.', 
                5, True)
            
            # Set validation message
            cmd.setDialogInitialSize(600, 400)
            cmd.setDialogMinimumSize(500, 350)
            cmd.okButtonText = "Create Next Batch of Bolts"
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('The DESIGN workspace must be active when running this script.')
            return
            
        commandDefinitions = ui.commandDefinitions
        # Check if the command exists and remove it
        cmdDef = commandDefinitions.itemById('BatchBolt')
        if cmdDef:
            cmdDef.deleteMe()
            
        # Create a new command definition
        cmdDef = commandDefinitions.addButtonDefinition('BatchBolt',
                'Create Batch of Bolts as STL',
                'Create a batch of unique bolts and export them as STL files (250 per batch, 1000 total).')
        
        # Connect to the command created event
        onCommandCreated = BatchBoltCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        
        # Execute the command
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # Prevent this module from being terminated when the script returns
        adsk.autoTerminate(False)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))