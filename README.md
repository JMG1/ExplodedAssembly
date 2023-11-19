# Exploded Assembly
FreeCAD workbench to create exploded views and animations of assemblies.

![ExplodedAssembly Icon](https://cloud.githubusercontent.com/assets/4140247/26527312/3388059a-435f-11e7-8317-10e041f18d35.PNG) The Exploded Assembly icon. 

![show](https://cloud.githubusercontent.com/assets/4140247/26527729/1cde4544-4368-11e7-9c85-03f974680ad8.PNG)

Watch a [screencast of Exploded Assembly](https://www.youtube.com/watch?v=lzYR7I2h7KQ)

**Important note: This repository replaces the now obsolete (https://github.com/JMG1/FreeCAD_ExplodedAssemblyAnimationWorkbench)**

### Features
* Create nice explosions of assemblies graphically (no code at all!)   
* Create sub-exploded groups   
* Give rotation to screws and nuts for realistic disassembles   
* Use the provided auxiliary assembly tools to place your parts together   
* TODO feature: create trajectory from wires and sketches   

### Installation
##### Automatically via Addon Manager (Recommended)
As of FreeCAD v0.17.9944 the new Addon Manager has been merged. Install this addon by:   
- Opening **Tools** > **Addon Manager** 
- Locating **ExplodedAssembly** and installing.  
- Relaunching FreeCAD.   

##### Manually install using git
Instructions for Ubuntu & Mint specifically but can be adapted to other distros. 
- Open the command prompt (terminal) with the keys **ctrl+alt+t**   
- Install git:  ***sudo apt-get install git***   
- Clone repository:  ***git clone https://github.com/JMG1/ExplodedAssembly ~/.FreeCAD/Mod/ExplodedAssembly***   
- Relaunch FreeCAD (workbench should be incorporated automagically).  

##### Manually install via ZIP
- Download https://github.com/JMG1/ExplodedAssembly as a ZIP (click 'Clone or Download' button)   
- For Ubuntu, Mint and similar OS's, extract it inside */home/username/.FreeCAD/Mod*   
- For Windows, extract it inside *drive: \Users\your_user_name\AppData\Roaming\FreeCAD\Mod*   
Then  
- Relaunch FreeCAD (workbench should be incorporated automagically).

### Basic usage

#### Run example file
1. Check the provided 'example.fcstd'.  
2. Load the workbench and then click on "Load Example File" inside the workbench drowpdown menu.

![example file](https://cloud.githubusercontent.com/assets/4140247/26527781/1ea3f7ba-4369-11e7-90cb-2c85a09e878f.PNG)

Watch the [Exploded Assembly workflow screencast](https://www.youtube.com/watch?v=t72qdG772Q8&feature=youtu.be). 

#### Create Simple Group
#### To explode a single object:
1. Select the objects you want to explode
2. If the selected object is of type "Body", the selected face will be used as a normal 
3. If you want to explode an object of type "Part" (contains other objects), select the Part object and then a face to be used as normal vector.
4. Several parameters can be modified at the properties of the single group (direction, speed, rotation...)

##### To explode several objects 
1. Select the objects you want to explode  in the same direction (type of objects allowed are Body and Part)
2. Select one face to use its normal as direction
3. Press the icon **Create Simple Group**
4. You can change the direction vectors and other parameters at the properties of the single group

#### Create Bolt Group
Bolt groups allow to rotate several screws/nuts/bolts around its own axis while moving. To create a Bolt Group:
1. Select one circular edge of each the bolts you want to animate
2. Select one face (arbitrary shape) wich has as normal vector in the direction in wich you want to move the selected bolts
3. Press the icon **Create Bolt Group**
4. You can change the direction vectors and other parameters at the properties of the single group


### Documentation
Wiki documentation will be available soon.
  
### Feedback 
For bugs please open a ticket in the [issue queue](https://github.com/JMG1/ExplodedAssembly/issues). For discussion please use the [dedicated Exploded Assembly thread](https://forum.freecadweb.org/viewtopic.php?f=24&t=9028) in the FreeCAD forums.

#### License 
GPLv2.0

#### Author
Javier Martínez @JMG1



