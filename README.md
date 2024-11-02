# Create Stop-Motion Animation Using Quadtree in Excel

## Project Overview
This project applies the **Quadtree** data structure to create a **Stop-Motion Animation** in an Excel file. The project takes a video input, processes each frame using the Quadtree algorithm to simplify and create an artistic effect on the images, and then saves each processed frame into separate sheets in an Excel file. Finally, a VBA (Macro) code will be used to cycle through the sheets, simulating video playback.

## Workflow
1. **Process Input Video**:
   - Split the video into individual frames.
   - Process each frame using the Quadtree algorithm to simplify the image while retaining important features.
   - Save the pixel data of each frame along with color information.

2. **Create Frames in Excel**:
   - Create an Excel file and write each frame into separate sheets.
   - Apply colors to the cells in the sheet to recreate the image of the frame.

3. **Play Stop-Motion Animation**:
   - Use the provided VBA Macro to cycle through the sheets, creating a video playback effect.

## Directory Structure
```
project-directory/
│
├── data/
│   ├── quadtrees.pkl               # Pickle file containing processed quadtree data
│   └── MatrixView.xlsx             # Excel file created with animation frames
│
├── src/
│   └── QuadTree.py                 # Contains the Quadtree class and related functions
│
├── main_script.py                  # Main Python script to process video and create Excel
├── README.md                       # Project documentation
└── VBAAnimationCode.txt            # Contains VBA code to play the animation
```

## Requirements
- **Python Libraries**:
  - `openpyxl` for manipulating Excel files
  - `pickle` for reading serialized data
  - `Pillow` (PIL) for image processing
- **Excel**:
  - Excel 2010 or later (supports Macros)

## How to Run the Project
1. **Install Requirements**:
   - Install Python and the necessary libraries.
   - Ensure you have Excel installed on your machine to open the created Excel file.

2. **Run the Python Script**:
   - Execute the main script to read input data, process frames, and create the Excel file:
     ```bash
     python main_script.py
     ```

3. **Run the VBA Macro**:
   - Open the `MatrixView.xlsx` file in Excel.
   - Load and run the VBA code in `VBAAnimationCode.txt` to create the stop-motion effect.

## VBA Code
Copy and paste the following VBA code into the VBA editor in Excel to cycle through the sheets for the animation effect:

```vba
Sub PlayAnimation()
    Dim sheet As Worksheet
    Dim delay As Double
    delay = 0.1  ' Delay (seconds) between frames
    
    Do
        For Each sheet In ThisWorkbook.Sheets
            sheet.Activate
            Application.Wait Now + TimeValue("00:00:" & delay)
        Next sheet
    Loop
End Sub
```

## Future Improvements
- Integrate real-time creation of Excel files from video.
- Enhance the Quadtree algorithm for faster processing.
- Add a user interface option to customize depth and display properties.

## License
This project is open-source and free to use under the [MIT License](LICENSE).
