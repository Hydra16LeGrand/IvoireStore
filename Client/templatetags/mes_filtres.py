from django import template
from Client import models
from datetime import date
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from random import randrange
register = template.Library()

@register.filter(name='multiplication')
def multiplication(a, b):
	return a*b


@register.filter()
def division(a, b):
	return a/b

@register.filter()
def soustraction(a, b,c):

	return b-a-c


@register.filter(name='filtre')
def filtre(model, parametre):

	resultat = model.filter(parametre=parametre)
	return resultat

@register.filter()
def filtre_historique_paiement_vendeur(cmd, produit):

	panier_produit =[]
	for pp in cmd.panierproduit_set.filter(produit=produit):
		panier_produit.append(pp)

	return panier_produit
	
@register.filter()
def affectation(a, b):
	b=a

@register.filter()
def prix_quantite(prix, quantite):

	return prix, quantite

@register.filter()
def calcul_montant(prix_quantite, commission):

	prix, quantite = prix_quantite

	return prix*quantite*(1-commission/100)


@register.simple_tag()
def calcul_montant_2(prix, quantite, commission):

	return prix*quantite*(1-commission/100)


@register.filter()
def differentes_commandes(historiques):

	num_cmd = []
	differentes_commandes =[]
	for historique in historiques:

		if not historique.num_cmd in num_cmd:
			num_cmd.append(historique.num_cmd)
			differentes_commandes.append(historique)

	return differentes_commandes


@register.filter()
def taille(liste):

	return len(liste)


@register.filter()
def conversion_date_jour(date):

	la_date = date.today() - date
	return la_date.days

@register.filter()
def sous_total(panier_produit):

	sous_total = 0
	for pp in panier_produit:
		sous_total += pp.quantite * pp.produit.prix

	return sous_total

@register.filter()
def retourner_client(username, colonne):

	user = User.objects.get(username=username)
	client =  models.User.objects.get(user= user)
	return client.adresse

@register.filter()
def reccup_produit_cmd(num_cmd):

	historiques = models.Historique.objects.filter(num_cmd=num_cmd)
	return historiques

@register.simple_tag()
def reccup_image_produit_cmd(libelle, categorie, prix_vendeur, prix):

	try:
		produit = models.Produit.objects.get(libelle=libelle, categorie=categorie, prix_vendeur=prix_vendeur, prix=prix)
	except:
		return "https://firebasestorage.googleapis.com/v0/b/projet-commerce.appspot.com/o/produit_introuvable.jpeg?alt=media&token=e0b8e248-ac8d-476d-b222-47d485f18f88"
	else:
		return produit.image


@register.filter()
def verif_existance_livreur(livreur):

	if livreur:
		return True
	else:
		return False

@register.filter()
def promo(temp):
	promo = date(2021, 10, 31) - date.today()
	return promo.days


@register.filter()
def parse_int(prix):

	return int(prix)

@register.filter()
def nbre_pp(requete):

	try:
		user = models.User.objects.get(user = User.objects.get(username=requete.user))
		panier = models.Panier.objects.get(user=user)
	except Exception as e:
		# logout(requete)
		id_panier_session = requete.session.get('id_panier_session', None)
		print(id_panier_session)
		if id_panier_session:
			# logout(requete)
			panier = models.Panier.objects.get(id = id_panier_session)
		else:
			return 0

	nbre_pp = 0
	for pp in models.PanierProduit.objects.filter(panier=panier).exclude(status=1):
		if not pp.produit.quantite <= 0:
			nbre_pp += 1

	return nbre_pp		


@register.filter()
def nbre_pu(requete):

	try:
		user = models.User.objects.get(user = User.objects.get(username=requete.user))
		envie = models.Envie.objects.get(user = user)
	except Exception as e:
		# logout(requete)
		id_envie_session = requete.session.get('id_envie_session', None)
		if id_envie_session:
			envie = models.Envie.objects.get(id = id_envie_session)
		else:
			return 0
				
	nbre_pu = 0
	for pu in models.EnvieProduit.objects.filter(envie = envie):
		if not pu.produit.quantite <= 0:
			nbre_pu += 1

	return nbre_pu


@register.filter()
def obtenir_profil(requete):

	try:
		user = models.User.objects.get(user = User.objects.get(username=requete.user))
	except Exception as e:
		logout(requete)
	else:
		return user.profil

@register.filter()
def prix_barre(produit):

	prix_barre = produit.prix + produit.prix * produit.categorie.commission/100
	return prix_barre


@register.filter()
def virgule(prix):

	prix = list(str(prix))
	prix_r = []
	for i in range(len(prix)):
		prix_r.append(prix[-1])
		del prix[-1]

	d=[]
	e=0
	for i in "".join(prix_r):
	    if e == 0:
	            d.append(i)
	            e+=1
	    else:
	            if e%3 == 0:
	                    d.append(',')
	                    d.append(i)
	            else:
	                    d.append(i)
	            e+=1
	for i in range(len(d)):
		prix.append(d[-1])
		del d[-1]
	return "".join(prix)

@register.filter()
def taille_detail(liste):

	iteration = []
	for i in range(len(liste)):
		iteration.append(i)

	return iteration

@register.filter()
def etoile_random(rien):

	nbre_etoile = randrange(3, 6)
	liste = list()
	for i in range(nbre_etoile):
		liste.append(i)
	return liste


@register.filter()
def prix_economie(prix_barre, prix):

	return int(prix_barre-prix)