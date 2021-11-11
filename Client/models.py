from django.db import models
from django.contrib.auth.models import User as User_p
# Create your models here.

# La table d'enregistrement des vendeurs
class Vendeur(models.Model):

	profil = models.TextField(null=True, blank=True, default="https://firebasestorage.googleapis.com/v0/b/projet-commerce.appspot.com/o/profil_inconnu.jpg?alt=media&token=4348dcfd-89c9-4c74-8a9c-65d75e6fadb5")
	# contact1 = models.CharField(max_length=20)
	# contact2 = models.CharField(max_length=20, blank=True, null=True)
	# ville = models.CharField(max_length=20)
	# commune = models.CharField(max_length=20, blank = True, null = True)
	# quartier = models.CharField(max_length=20)
	adresse = models.CharField(max_length=255)

	produits_vendu = models.TextField(blank=True, null=True)

	# Liaison un a un avec la table User
	user = models.OneToOneField(User_p, on_delete=models.CASCADE)
	# Methode qui va permettre de reccuperer le profil du vendeur
	# def get_profil(self):

	# 	if self.profil and hasattr(self.profil, 'url'):
	# 		return self.profil.url
	# 	else:
	# 		return "/media/profil_vendeur/profil_inconnu.jpg"	

	def __str__(self):

		return self.user.username

# Table categorie
class Categorie(models.Model):

	nom = models.CharField(max_length=50)
	# cle est le nom de code de la categorie
	cle = models.CharField(max_length=50)
	# Frais lie a cette categorie
	commission = models.FloatField()

	# Cette methode retournera le nom de la methode et les frais lorsqu'on voudra une categorie
	def __str__(self):
		return self.nom



class Produit(models.Model):

	
	libelle = models.CharField(max_length = 200)
	description = models.TextField()
	prix_vendeur = models.FloatField()
	prix = models.FloatField()
	quantite = models.IntegerField()
	
	# Minimum order quantity
	# moq = models.IntegerField(default=1)

	# Permettant de definir si le produit est disponible ou pas
	status = models.BooleanField()
	image = models.TextField(default="https://firebasestorage.googleapis.com/v0/b/projet-commerce.appspot.com/o/produit_introuvable.jpeg?alt=media&token=e0b8e248-ac8d-476d-b222-47d485f18f88")
	date_ajout = models.DateField(auto_now_add=True)
	date_modification = models.DateField(auto_now=True)
	# Liaison un a plusieurs avec la table vendeur
	vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
	# Liaison un a plusieurs avec la table vendeur mais la colonne peut ne pas etre renseigner 
	categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.libelle

	# def get_image(self):
	# 	if self.image and hasattr(self.image, 'url'):
	# 		return self.image.url
	# 	else:
	# 		return "media/image_produit/pas_d_image.jpg"


# La classe servant a enregistrer des images supplementaires de produit 
class ImageProduit(models.Model):

	produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
	image = models.TextField(default="https://firebasestorage.googleapis.com/v0/b/projet-commerce.appspot.com/o/produit_introuvable.jpeg?alt=media&token=e0b8e248-ac8d-476d-b222-47d485f18f88")

	# def get_image(self):
	# 	if self.image and hasattr(self.image, 'url'):
	# 		return self.image.url
	# 	else:
	# 		return "media/image_produit/pas_d_image.jpg"


# La classe d'enregistrement des clients. J'aurai du l'appeler client Pfff.
class User(models.Model):

	# contact1 = models.CharField(max_length=20)
	# contact2 = models.CharField(max_length=20, blank=True, null = True)
	# ville = models.CharField(max_length=20)
	# commune = models.CharField(max_length=20, blank = True, null = True)
	# quartier = models.CharField(max_length=20)
	adresse = models.CharField(max_length=255)
	profil = models.TextField(null=True, blank=True, default="https://firebasestorage.googleapis.com/v0/b/projet-commerce.appspot.com/o/profil_inconnu.jpg?alt=media&token=4348dcfd-89c9-4c74-8a9c-65d75e6fadb5")
	# Relation plusieurs a plusieurs avec produits. avec le widget through nous allons redefinir la nouvelle relation creer
	# Remarque, Cette redefinition n'est pas obligatoire. Mais je l'ai fait au cas ou je voudrais ajouter de nouvelles colonnes
	produit = models.ManyToManyField(Produit, through="ProduitUser")
	# Liaison un a un avec la table User
	user = models.OneToOneField(User_p, on_delete=models.CASCADE)

	# def get_profil(self):

	# 	if self.profil and hasattr(self.profil, 'url'):
	# 		return self.profil.url
	# 	else:
	# 		return "/media/profil_client/profil_inconnu.jpg"

	def __str__(self):

		return self.user.last_name

class Envie(models.Model):

	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	produit = models.ManyToManyField(Produit, through="EnvieProduit")

# La classe resultante de produit et de client pour gerer les envies
class ProduitUser(models.Model):

	produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

# La classe resultante de produit et de envie pour gerer les envies
class EnvieProduit(models.Model):

	envie = models.ForeignKey(Envie, on_delete=models.CASCADE)
	produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

# La classe des livreurs
class Livreur(models.Model):

	nom = models.CharField(max_length=50)
	prenom = models.CharField(max_length=50)
	contact = models.CharField(max_length=10)
	cin = models.CharField(max_length=30)
	# la valeur est 1 si le livreur est toujours de service, 0 sinon
	existance = models.BooleanField(default=1)
 
	def __str__(self):

		return self.nom+" "+self.prenom

class Panier(models.Model):

	user = models.OneToOneField(User, on_delete = models.CASCADE, blank=True, null=True)
	produit = models.ManyToManyField(Produit, through="PanierProduit")

	# def __str__(self):

	# 	user = str(self.user.user.username)
	# 	return user

# La table pour enregistrer les commandes
class Commande(models.Model):

	status = [
	('pas_ok', "Commande annulée"),
	('ok', "Commande éffectué")]

	panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now=True)
	# status pour faire la difference entre une commande annulee et une commande ok
	status = models.CharField(max_length=20, choices=status, default='ok')
	montant = models.FloatField()

	code = models.IntegerField()


# Association resultante de panier et produit qui devient une table dont on va ajouter des colonnes
class PanierProduit(models.Model):

	panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
	produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
	commande = models.ForeignKey(Commande, on_delete=models.CASCADE, blank=True ,null=True)

	quantite = models.IntegerField(default=1)
	date_ajout = models.DateTimeField(auto_now_add=True)
	date_modification = models.DateTimeField(auto_now=True)
	# status qui differenciera les produits qui ne sont plus dans le panier et ceux qui y sont
	# Permettra egalement de faire l'historique des ventes des clients
	# 0 si la commande n'a pas encore ete finaliser 1 sinon
	status = models.BooleanField(default=0)


class Livraison(models.Model):

	status = [
		('en_cours', "En cours"),
		('annulee', "Annulée"),
		('faite', "Faite")]

	adresse_livraison = [
	('abidjan', "Livraison à abidjan"),
	('interieur', "Livraison à l'interieur du pays")]

	commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
	livreur = models.ForeignKey(Livreur, on_delete = models.CASCADE, blank=True, null=True)
	# Abidjan et l'interieur du pays sont les 2 choix possibles pour cette version de l'appli
	adresse_livraison = models.CharField(max_length=20, choices=adresse_livraison)
	frais = models.FloatField()
	date_livraison = models.DateField(blank=True)
	status = models.CharField(max_length=20, choices=status)


class Paiement(models.Model):
	status = [
		('en_attente', "En entente"),
		('refuse', "Réfusé"),
		('fait', "Fait")]

	moyen_paiement = [
	('cash_livraison', "Payer cash à la livraison")]

	commande = models.OneToOneField(Commande, on_delete=models.CASCADE)

	moyen_paiement = models.CharField(max_length=20, choices=moyen_paiement, default='cash_livraison')
	montant_total = models.FloatField()
	status = models.CharField(max_length=15, choices=status)

# Enregistrement de l'avis des clients apres avoir acheter un(des) produit(s)
class Avis(models.Model):

	note_produits = models.IntegerField()
	note_livraison = models.IntegerField()
	commentaire = models.TextField()
	date = models.DateTimeField(auto_now_add=True)

	livraison = models.OneToOneField(Livraison, on_delete=models.CASCADE)


class Historique(models.Model):

	status_livraison = [
	('en_cours', "En cours"),
	('annulee', "Annulée"),
	('faite', "Faite")]

	status_paiement = [
	('en_attente', "En entente"),
	('refuse', "Réfusé"),
	('fait', "Fait")]

	num_cmd = models.IntegerField()
	date_cmd = models.DateTimeField(auto_now_add=True)
	montant_cmd = models.FloatField()
	code_cmd = models.IntegerField()

	libelle = models.CharField(max_length=100)
	categorie = models.CharField(max_length=30)
	prix_vendeur = models.FloatField()
	prix = models.FloatField()
	quantite = models.IntegerField()

	frais_livraison = models.FloatField()
	adresse_livraison = models.CharField(max_length=100)
	status_livraison = models.CharField(max_length=20, choices=status_livraison, default='en_cours')
	livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE, blank=True, null=True)

	moyen_paiement = models.CharField(max_length=100)
	montant_total = models.FloatField()
	status_paiement = models.CharField(max_length=20, choices=status_paiement, default='en_attente')
	date_paiement = models.DateTimeField(null=True, blank=True)

	client = models.CharField(max_length=100)
	vendeur = models.CharField(max_length=100)