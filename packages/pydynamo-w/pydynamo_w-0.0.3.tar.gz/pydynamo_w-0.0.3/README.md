--- english version [below](#english) ---
# TPworld3
Un TP pour jouer avec le modèle World3 et découvrir tout un tas de concepts, qui peuvent servir pour comprendre les dynamiques de la croissance dans un monde fini.

# Installation
- Télécharger le TP à l'adresse <https://gitlab.inria.fr/abaucher/pydynamo/-/raw/TPworld3/TP.ipynb?inline=false>

## Option A: Avec le jupyterhub de l'UGA si vous avez un compte UGA
- Se connecter à <https://jupyterhub.univ-grenoble-alpes.fr> avec ses identifiants UGA
- Appuyer sur le bouton **upload** en haut à droite, et sélectionner le TP téléchargé
- Sur le menu **files**, lancer le notebook TP.ipynb en cliquant dessus

## Option B: Autrement, en local sous Linux
- Il faut avoir Python3 
- Le module a été testé sous Ubuntu 24
### Créer un environnement virtuel
- Il est préférable d'utiliser un environnement virtuel, qui assure les bonnes versions des librairies.
- Pour installer et créer un nouvel environnement virtuel sous le nom de *dnovenv*:
```
sudo apt install python3.12-venv
python3.12 -m venv dnovenv
```
Pour l'activer, si on est dans le dossier qui contient le dossier `dnovenv`, il faut rentrer: 
```
source dnovenv/bin/activate
```
 et peut on le désactiver avec `deactivate`.

### Installer le TP
- Ouvrir un terminal, puis installer jupyter et activer les extensions:
```
python3 -m pip install --upgrade ipykernel jupyter jupyter_contrib_nbextensions notebook==6.4.12
```
- Ouvrir le TP.ipynb avec `jupyter-lab TP.ipynb`.

# Jouer
Dans le notebook TP.ipynb, des textes et morceaux de codes montrent l'idée et le fonctionnement de *Pydynamo* et du modèle World3. On peut faire différentes expériences de simulation en changeant des paramètres, et étudier certains phénomènes.

--- english version ---
# English
# Tpworld3
A practical session to play with the World3 model and discover many interesting concepts that can be useful to understand the dynamics of growth in a finie world.

# Installation
- Download the notebook at the adress: <https://gitlab.inria.fr/abaucher/pydynamo/-/raw/TPworld3/TP_en.ipynb?inline=false>

## Option A: With UGA (Univ-Grenoble_Alpes) **jupyterhub** if you have an UGA account
- Login to <https://jupyterhub.univ-grenoble-alpes.fr> with your agalan id
- Click on the **upload** button at the top right and then select the notebook you downloaded
- On the **files** menu, click on the notebook to run it

## Option B: Otherwise, locally with linux
- You should have Python3.8 or more recent
- The notebook has been tested on Unbuntu20 and more
### Create a virtual environment
- It's better to use a virtual environment to store the librairies you'll use
- To install a new virtual environment named *dnovenv*:
```
sudo apt install python3.12-venv
python3.12 -m venv dnovenv
```
To activate it, if you are in the folder that contains the `dnovenv` folder, type::
```
source dnovenv/bin/activate
```
 et peut on le désactiver avec `deactivate`.

### Install the notebook
- Open a terminal, and the install jupyter and activate the extensions:
```
python3 -m pip install --upgrade ipykernel jupyter jupyter_contrib_nbextensions notebook==6.4.12
```
- Open the notebook with `jupyter-lab TP_en.ipynb`.

# Play
In the TP_en.ipynb notebook, there is texts and code cells that explain how the *pydynamo* module and the World3 model works. We cans run different simulations, change parameters and analyse some phenomenon.

