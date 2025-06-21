<img src="media\overview.jpg"></img>

# Mesh from SDF
Add-on for mesh modeling with SDF in Blender.

<video src="https://github.com/user-attachments/assets/b20142b3-20d9-4de1-8d97-927f9eca7366"></video>

## Features

- Primitives
  - [x] Box
  - [x] Sphere
  - [x] Cylinder
  - [x] Torus
  - [x] Cone
  - [x] Pyramid
  - [x] Truncated Pyramid
  - [x] Hexagonal Prism
  - [x] Triangular Prism
  - [ ] Spline
  - [x] Distance Function (External files written in GLSL format)
- [x] SDF to Mesh Conversion (Based on Marching Cube)
- Boolean Operations 
  - [x] Union
  - [x] Diffrence
  - [x] Intersection
- Blend Types
  - [x] No Blending
  - [x] Smooth
  - [x] Champfer
  - [x] Steps
  - [x] Round
- [ ] Mirror
- [ ] Repeat
- [x] Visualization of bounding boxes

## Screenshots

<img src="media/panel.png" width="256"><img/>


## Requirements
- Blender 4.x (Development and testing is being done with this Blender version)
- Windows 10 / 11 (Not tested on MacOS and Linux)

## Dependent packages
- [moderngl](https://github.com/moderngl/moderngl)

## Installation
1. Drag and drop the zip file downloaded from the repository release page into Blender to install.
2. Activate the installed add-on (mesh_from_sdf) in `Edit/Preference/Add-ons`.

## Start up
1. Select `SDF2Mesh` from the toolbar to open the add-on hierarchy panel.
2. Changed `RenderEngine` to `MeshFromSDF`
3. Switch the 3D View render mode to `Render` or `Material`.
4. Pressing the reload button displays the SDF objects registered in the hierarchy (Do this the first time you start Blender or activate this add-on).

## Known Issue
- Undo processing is not implemented for Gizmo operations on SDF primitives.
  - While it is possible to always invoke Undo while dragging Gizmo, ideally, Undo should be executed only when the drag ends.
- After changing the type of the SDF primitive once, the previous Gizmo operation is reset when it is changed back again.
