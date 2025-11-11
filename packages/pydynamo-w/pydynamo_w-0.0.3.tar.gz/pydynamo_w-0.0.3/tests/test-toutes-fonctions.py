from pydynamo import World3

# Commande pour importer et utiliser en direct une bibliothèque graphique
import matplotlib.pyplot as plt

# Déclaration d'une instance du premier (=1) scénario du modèle world3
w = World3(1)

# Lancement de la simulation, par défaut de 1900 à 2100
w.run()

# Affichage de l'évolution principales variables du monde, avec un titre
w.plot_world(title="Scénario 1: Business as usual")
plt.show()

w.equation('al')

# Affichage des variables al, io et nr, renormalisé (rescale) entre 0 et 1
w.plot(['al', 'io', 'nr'], rescale=True)

plt.show()

# Afficher la définition et l'équation de 'io'
print(w.definition('io'))
print(w.equation('io')) 
# Affichage des variables désirées, normalisé (rescale) entre 0 et 1, avec un titre
w.plot({'io', 'ic', 'fcaor', 'cuf', 'icor'}, rescale=True, title="Quelques variables en jeu dans le calcul du produit industriel")

plt.show()


print(w.equation('jph'))
w.plot_non_linearity('jph')

plt.show()

print(w.definition('jpht'))
print(w.jpht)


print(w.equation('fcaor'))
print(w.equation('fcaor1'))
print(w.definition('nrfr'))
w.plot_non_linearity('fcaor')
plt.show()

w_pas_de_gachis = World3(1)
print(w_pas_de_gachis.pl)
w_pas_de_gachis.pl = 0
w_pas_de_gachis.run()
w['pop', 2050]


wr2 = World3(scenario_number=1)
print(wr2.nri)

# Changement de valeur !
wr2.nri = 2*wr2.nri

wr2.run()
wr2.plot_world(title="Scénario avec 2 fois plus de ressources initiales")
plt.show()


w.show_influence_graph(variables=['pal', 'al'], depth = 1).show('exemple.html')

# Comparaison des systèmes w et w_pas_bcp_de_terres sur les variables f et al
w.plot_compare(w_pas_de_gachis, {'f', 'al'}, rescale=True)
plt.show()

# Affichage des variables sortantes de ppolx, avec leurs définitions respectives
print(w.get_out_nodes('ppolx', with_definitions=True))

# Affichage du graphique
w.show_influence_graph(variables='ppolx').show("exemple.html")
plt.show()

# Comparaison des systèmes w et wr2 sur différentes variables
w.plot_compare(wr2, w.get_out_nodes('ppolx'), rescale=True, title="Comparaison des scénarios 1 et 2 pour des variables liées à la pollution")
plt.show()


# Comparaison des systèmes w et wr2 sur différentes variables
w.plot_compare(wr2, {'ppolx', 'lmp', 'lfert'}, rescale=True, title="Comparaison des scénarios 1 et 2 pour des variables liées à la pollution")
plt.show()


# Une nouvelle instance du modèle assez burlesque
# Par défaut, cette commande prend le scénario 2, le plus 'réaliste' aujourd'hui
w_burlesque = World3()
# À partir de 1985, suite à des ateliers efficaces, on ne gâche plus de nourriture 
w_burlesque.new_politic('pl', 1985, 0)
# À partir de 2052, à cause de la 8G, la terre assimile moins bien la pollution
w_burlesque.new_politic('ahlmt', 2052, w.ahlmt/2)
# À partir de 2012, par miracle, l'indice de pollution persistente ppolx décroit de 2% par an
w_burlesque.new_politic('ppolx', 2012, 'ppolx.j - 0.02*ppolx.j*dt')
# Simulation et affichage
w_burlesque.run()
w_burlesque.plot(['pl', 'ahlm', 'ppolx'], rescale=True)
plt.show()

# Affiche l'évolution la pollution et la génération de pollution pour le scnéario 2 
wr2 = World3() # Par défaut, le scénario de World3 est le second, car c'est le plus "réaliste"
wr2.run() 
wr2.plot(['ppol', 'ppgr'], rescale=True, title='La pollution du scénario 2')
plt.show()

 # Afficher l'équation et les définitions des variables utilisées pour le calcul de la génération de pollution ppgr
print(wr2.equation('ppgr'))
print(wr2.get_in_nodes('ppgr', with_definitions=True))
# Afficher les différents facteurs de polutions, sans rescale pour pouvoir comparer
wr2.plot(['ppgr', 'ppgio', 'ppgao', 'ppgf'], title="Facteurs de pollution dans le scénario 2")
plt.show()


print(wr2.equation('ppgao'))
print(wr2.get_in_nodes('ppgao', with_definitions=True))
print(wr2.equation('aiph'))
print(wr2.get_in_nodes('aiph', with_definitions=True))

print("Valeurs des constantes à changer:", wr2.fipm, wr2.amti)
print("Équation de falm:", wr2.equation('falm'))
print("Valeur de falmt:", wr2.falmt)
wr2.plot_non_linearity('falm')
plt.show()

w_bio = World3()

# Changement de politique !
w_bio.new_politic('fipm', 2020, w.fipm/2) # Moins de matériel persistent
w_bio.new_politic('amti', 2020, w.amti/2) # Moins toxique
w_bio.new_politic('falmt', 2020, w.falmt*2) # Plus de maintenance (et donc moins d'intrants)

# Simuler et afficher
w_bio.run()
w_bio.plot_world(title="Scénario du passage au bio")
plt.show()

plt.figure(figsize=(10, 5)) # Augmente la taille de la figure pour y voir plus clair
wr2.plot_compare(w_bio, ['nr', 'iopc', 'fpc', 'le', 'ppolx'], rescale=True, title="Passage au bio: quelques différences clés")
plt.show()

print(w_bio.equation('f'))
wr2.plot_compare(w_bio, w_bio.get_in_nodes('f'), rescale=True, title="La chute de nourriture dans le passage au bio")
plt.show()

print(w.equation('al'))
w_bio.plot(['ldr', 'ler', 'lrui'], title="Les variables en jeu dans la mise en culture agricole")
plt.show()

print(w.equation('ldr'))
w_bio.plot(['tai', 'fiald', 'dcph'], rescale=True, title="Enjeux économiques agricoles")
plt.show()

print(w_bio.equation('dcph'))
print(w_bio.get_in_nodes('dcph', with_definitions=True))
w_bio.plot_non_linearity('dcph')
plt.show()

# Affiche l'ensemble des utilisation de terres
w_bio.plot(['al', 'pal', 'pali', 'uil'], title="Utilisation des terres dans le scénario bio")
plt.show()

# Copie du scénario "décroissance"

w_dec = World3()
w_dec.new_politic('io', 2002, 'io.j  - 0.05*dt*io.j')
w_dec.run()
w_dec.plot_world(title="Scénario de décroissance industrielle")

w_viable = w_dec.copy()

# Santé autonome
w_viable.new_politic('hsapct', 2002, [100, 130, 150, 165, 180, 210, 220, 235, 230])
# Agriculture sans intrants
w_viable.new_politic('lymct', 2002, [w_dec.get_at('lymc', 2000) for _ in range(len(w_dec.lymct))])
# Nature urbaine
w_viable.new_politic('cmit', 2002, w_dec.cmit*0)
# Agro-écologie
w_viable.llmytm = 2002
w_viable.new_politic('llmy2t', 2002, [1 for _ in range(len(w_dec.llmy2t))])
# Stabilisation des naissances
w_viable.zpgt = 2002
w_viable.fcest = 2002

# Simulation et affichage !
w_viable.run()
w_viable.plot_world(title="Deuxième réunion des alternatives")
plt.show()
