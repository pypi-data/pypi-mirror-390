# The Frame Framework  
![python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white) ![dev](https://img.shields.io/badge/Development-By_pt-ff002f) ![status](https://img.shields.io/badge/Status-Alpha-00cc52) ![rights](https://img.shields.io/badge/Rights_holder-Intelektika--team-b100cc) ![design](https://img.shields.io/badge/PyPI_name-frame--fwl-F2A400)

Frame is a multifunctional framework that combines concepts implemented as separate packages.  

| Concept | Short Descripton | Terms | Version |  
| :--- | :--- | :--- | :--- |  
| Frames | Creating isolated contexts for code execution and configuration. | Frame, Framing, Framefile, Superglobal | 0.4.12 |  
| Nets | Cryptography, white/gray hacking, and internet security. | None yet | 0.1.1 |  

### Quick Start -
```bash 
pip3 install frame-fwl
```
Import like `frame`.


## 🚀 Detailed Concept Descriptions  
### 🖼 Frames  
This concept aims to simplify code transfer, serialization, and configuration.  

#### **Key Features** -  
  - **Framer** - Low-level frame implementation used as the foundation for abstractions.  
  - **Var, Get, Exec, Return, Code, SystemOp** - Low-level functions for direct interaction with Framer.  
  - **Frame** - High-level API for working with the concept.  
  - **FramesComposer** - Combines frames into a unified system for efficient operation.  

#### **Terms** -  
  - **Frame** - An isolated execution space with its own variables and code. Can interact with other contexts.  
  - **Framing** - Creating a local environment with superglobal variables.  
  - **Superglobal** - The state of an object when it does not depend on the context. Roughly speaking, a global frame.  
  - **Framefile** - A binary frame image that can be saved and loaded.  

#### **Example Demonstrating the Concept’s Utility** -  

Suppose we have a configuration file for a simple neural network:  
```python  
koeff = 0.5  
learning_rate = 0.04  
test_input = 'test'  
epochs = 2000  
batch_size = 256  
def not_for_import():...  
```  
This means the main file would require:  
```python  
from config import test_input, epochs, batch_size, koeff, learning_rate  
print(test_input)  
```  
This is incredibly inconvenient! Importing requires remembering variable names and writing long import statements.  
Here’s how it looks using the Frame concept:  
```python  
from frame import Frame  
sgc = Frame() # superglobal context  
sgc.Var('koeff', 0.5, 'float')  
sgc.Var('learning_rate', 0.04, 'float')  
sgc.Var('batch_size', 256, 'int')  
sgc.Var('epochs', 2000, 'int')  
sgc.Var('test_input', 'test', 'str')  
def not_for_import():...  
```  
Now, the main file simply imports the context:  
```python  
from config import sgc  
print(sgc.Get('test_input'))  
```  
This is much simpler and cleaner!  

Latest version will installed with framework to frame.frame_core.

## ✨ Key Features

### 🎭 Multiple Contexts
- Isolated execution environments  
- Inter-context communication
- Superglobal variables system

### 🔧 Developer Experience  
- High-level API with Frame class
- Low-level control with Framer
- Plugin system for extensions

### 💾 Serialization & Storage
- Save/Load frames to JSON/Pickle
- Binary framefile format
- Cross-session state persistence

### 🌐 Nets  
This concept is in its early stages. It will include modules for cryptography, internet security, and white/gray hacking tools for educational ONLY purposes.

Currently, the concept is in development. Latest version will installed with framework to frame.nets_core.

## 🔗 Links
- [Our Team](https://github.com/Intelektika-team/)
- [Main developer](https://github.com/pt-main)
