from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
import random
import pyrebase
from django.core.mail import send_mail
from django.core.cache import cache
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse, resolve
# import firebase_admin
from . import models
# from firebase_admin import credentials, storage

# Create your views here.

# Les Configurations Firebase pour l'authentification et l'inscription des clients
firebaseConfig = {
    "apiKey": "AIzaSyAcIgIdfW6JQOwi7fVjsPV54ouOVfBQgdI",
    "authDomain": "projet-commerce.firebaseapp.com",
    "databaseURL": "https://projet-commerce.firebaseio.com",
    "projectId": "projet-commerce",
    "storageBucket": "projet-commerce.appspot.com",
    "messagingSenderId": "647035456259",
    "appId": "1:647035456259:web:2c61b586513be282fff736",
    "measurementId": "G-4XKQVRYXT9"
    }
# firebaseConfig = {
#     "storageBucket": "projet-commerce.appspot.com",
#     }

# cred = credentials.Certificate("projet-commerce-firebase-adminsdk.json")
# default_app = pyrebase.initialize_app(firebaseConfig)
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# Fonction permettant d'ajouter des produits qui sont dans la session au panier lorsque l'utilisateur se connecte
# Cela est fait parceque a la deconnexion, toutes les donnees de session sont supprimees.
def maj_session(id_session, panier=None, envie=None):

	if panier:
		panier_produit_session = models.PanierProduit.objects.filter(
			panier = models.Panier.objects.get(id = id_session)
		)

		for pps in panier_produit_session:
			pps.panier = panier
			pps.save()

	if envie:
		envie_produit_session = models.EnvieProduit.objects.filter(
			envie = models.Envie.objects.get(id = id_session)
		)

		for eps in envie_produit_session:
			eps.envie = envie
			eps.save()

# Classe permettant de gerer le systeme d'authentification du client
class Acces:

	def inscription(request):

		if request.method == "POST":
			form = request.POST
			print("Ici")
			try:
				user = User.objects.get(username=form.get('username'))
			except Exception as e:

				try:
					user = User.objects.create_user(
						username=form.get('username'), 
						password=form.get('mdp'),
						last_name=form.get('nom'),
					)

				except Exception as e:
					return render(request, "Client/authentification.html", {
												'message': ("Erreur lors de la création du compte.\n"
													"Si cela persiste Veuillez contacter le service client au 0556748529")
												})
				else:
					try:
						client = models.User.objects.create(
							adresse = form.get('adresse'),
							user = user)
					except Exception as e:
						user.delete()
						return render(request, "Client/authentification.html", {
												'message': ("Erreur lors de la création du compte.\n"
													"Si cela persiste Veuillez contacter le service client au 0556748529")
												})
					else:

						models.Panier.objects.create(user=client)
						models.Envie.objects.create(user=client)
						user = authenticate(username=form.get('username'), password=form.get('mdp'))
						if user is not None:
							login(request, user)
							if form.get('next'):
								print("next :", form.get('next'))
								return HttpResponseRedirect(form.get('next'))

						return render(request, "Client/authentification.html", {
							'message_success': "Votre compte a été creer avec succès",
							'redirect_to':form.get('next')})
			else:
				return render(request, "Client/inscription.html", {
					'message': "Un compte est déja associé à ce nom d\'utilisateur ou cet email", 'form': form})
					
		else:
			
			redirect_to = request.GET.get('next')
			if redirect_to:
				return render(request, "Client/inscription.html", {'redirect_to': redirect_to})
			return render(request, "Client/inscription.html")

	def authentification(request, message=None):

		if request.method == 'POST':
			form = request.POST
			# authenticate renvoi None si le auth_user n'existe pas et le champ de auth_user sinon
			try:
				client = models.User.objects.get(user=User.objects.get(username=form.get('username')))
			except:
				print("RED2 :", form.get('next'))
				return render(request, "Client/authentification.html", {'message':"Compte inexistant", 
																		"redirect_to": form.get('next')})
			else:
				user = authenticate(username=form.get('username'), password=form.get('mdp'))
				if user is not None:
					login(request, user)
					if form.get('next'):
						return HttpResponseRedirect(form.get('next'))
					else:
						return redirect('dashboard_client')
				else:
					return render(request, "Client/authentification.html", {
						'message': "E-mail ou mot de passe incorrect"})

		else:

			redirect_to = request.GET.get('next')

			print("RED :", redirect_to)
			if not redirect_to:
				return render(request, "Client/authentification.html", {
					'message_infos': message
					})
			return render(request, "Client/authentification.html", {
				'message_infos': "Authentification Nécessaire", 
				'redirect_to':redirect_to})
			
	def deconnexion(request):

		redirect_to = request.GET.get('next')
		logout(request)

		if redirect_to is not None:
			return HttpResponseRedirect(redirect_to)
		else:
			return redirect('accueil')

class Panier:

	# @login_required(login_url="/authentification/")
	# @method_decorator(login_required)
	def ajouter(request, id_produit):

		if request.GET.get('vendeur'):
			kwargs = {'vendeur': request.GET.get('vendeur')}
		else:
			kwargs = dict()
		redirect_to = request.GET.get('next')
		redirect_to = resolve(redirect_to).url_name
		if not request.user.is_authenticated:

			try:
				produit = models.Produit.objects.get(id = id_produit)
			except Exception as e:
				raise e
			else:
				id_panier_session = request.session.get('id_panier_session', None)

				if id_panier_session:
					
					try:
						panier = models.Panier.objects.get(id = id_panier_session)
					except Exception as e:
						raise e
					else:
						try:
							models.PanierProduit.objects.get(panier = panier, produit = produit)
						except Exception as e:
							models.PanierProduit.objects.create(
								panier = panier,
								produit = produit
							)
							kwargs['message'] = "Produit ajoute au panier."
							return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))
				else:
					panier = models.Panier.objects.create()
					request.session['id_panier_session'] = panier.id

					try:
						models.PanierProduit.objects.get(panier = panier, produit = produit)
					except Exception as e:
						models.PanierProduit.objects.create(
							panier = panier,
							produit = produit
						)
						
						kwargs['message'] = "Produit ajoute au panier."
						return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))

			kwargs['message'] = "Cet article existe déja dans le panier."
			return HttpResponseRedirect(reverse(redirect_to, kwargs={'message': "Cet article existe déja dans le panier."}))

		else:
			try:
				
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
					produit = models.Produit.objects.get(id=id_produit)
				except Exception as e:
					raise Http404()
				else:
					# On tente de reccuperer le produit lie au panier. Histoire de voir s'il na pas encore ete ajoute
					try:
						panier_produit = models.PanierProduit.objects.get(produit=produit, panier=panier, status=0)
					except Exception as e:
						# Si le produit nest pas dans le panier on l'ajoute
						try:
							models.PanierProduit.objects.create(produit = produit, panier = panier)
						except Exception as e:
							return render(request, "Errors/500.html", status=500)
						else:
							if request.GET.get('vendeur'):
								return HttpResponseRedirect(reverse(redirect_to, kwargs={
																	'vendeur': request.GET.get('vendeur'),
																	'message': "Produit ajoute au panier."}))
							return HttpResponseRedirect(reverse(redirect_to, kwargs={'message': "Produit ajoute au panier."}))
					else:
						if request.GET.get('vendeur'):
							return HttpResponseRedirect(reverse(redirect_to, kwargs={
														'vendeur': request.GET.get('vendeur'),
														'message': "Cet article existe déja dans le panier."}))
						return HttpResponseRedirect(reverse(redirect_to, kwargs={
																			'message': "Cet article existe déja dans le panier."
																			}))

	def lister(request, message=None):

		id_panier_session = request.session.get('id_panier_session', None)
		if not request.user.is_authenticated:
			# return redirect("authentification", "Veuillez vous authentifier d\'abord")

			if id_panier_session:
				try:
					panier = models.Panier.objects.get(id = id_panier_session)
				except Exception as e:
					raise e
				else:
					panier_produit = models.PanierProduit.objects.filter(panier = panier, status=0)

			else:
				panier = models.Panier.objects.create()
				request.session['id_panier_session'] = panier.id
				panier_produit = models.PanierProduit.objects.filter(panier = panier)

		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
				except Exception as e:
					return render(request, "Errors/500.html", status=500)
				else:

					if id_panier_session:
						maj_session(id_session=id_panier_session, panier=panier)
					# Liste des produits dont on a pas confirmer la commande
					panier_produit = models.PanierProduit.objects.filter(panier=panier, status=0)

		# on exclue les produits dont la quantite est nulle
		for pp in panier_produit:
			if pp.produit.quantite <= 0:
				panier_produit = panier_produit.exclude(produit = pp.produit)
				pp.delete()

		# Le gain que baradjise-shop fera avec la vente. On l'utilisera pour traiter le montant minimum a commander
		gain = 0.0
		for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
			gain += pp.quantite*(pp.produit.prix-pp.produit.prix_vendeur)


		return render(request, "lister_panier.html",{
						'panier': panier, 
						'panier_produit': panier_produit, 
						'gain': gain, 
						'message_success': message,
						'active':"panier"}
						)

	# Suppression du produit du panier
	def supprimer(request, id_produit):


		if not request.user.is_authenticated:
			# return redirect("authentification", "Veuillez vous authentifier d\'abord")

			try:
				produit = models.Produit.objects.get(id = id_produit)
			except Exception as e:
				raise e
			else:
				id_panier_session = request.session.get('id_panier_session', None)

				try:
					panier = models.Panier.objects.get(id = id_panier_session)
				except Exception as e:
					raise e
				else:
					produit_a_supprimer = models.PanierProduit.objects.get(panier = panier, produit=produit)
					produit_a_supprimer.delete()
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
					produit = models.Produit.objects.get(id=id_produit)
					produit_a_supprimer = models.PanierProduit.objects.get(panier=panier, produit=produit, status=0)
				except Exception as e:
					raise Http404()
				else:
					produit_a_supprimer.delete()

		return redirect('lister_panier', "L\'article à bien été supprimé")

	# changer la quantite d'un produit dans le panier
	def modifier(request, id_produit):

		try:
			produit = models.Produit.objects.get(id=id_produit)
		except Exception as e:
			raise e
		else:
			form = request.POST
			if not request.user.is_authenticated:
				# return redirect('authentification',"Veuillez vous authentifier d\'abord")
				id_panier_session = request.session.get('id_panier_session', None)
				panier = models.Panier.objects.get(id = id_panier_session)
			else:
				try:
					client = models.User.objects.get(user=request.user)
					panier = models.Panier.objects.get(user=client)
				except Exception as e:
					return redirect("authentification")

			try:
				# On verifie si la quantite saisie n'est pas superieure a la quantite du produit
				# Cela a ete verifier egalement dans le template
				if produit.quantite >= int(form.get('quantite')):
					panier_produit = models.PanierProduit.objects.get(panier=panier, produit = produit, status=0)
					panier_produit.quantite = form.get('quantite')
				panier_produit.save()
			except Exception as e:
				raise Http404()
			else:
				return redirect('lister_panier', "La quantité à bien été changé")

	@login_required(login_url="/authentification/")
	def finaliser_commande(request):
		try:
			client = models.User.objects.get(user=request.user)
		except Exception as e:
			return redirect("authentification")
		else:
			try:
				panier = models.Panier.objects.get(user=client)
				id_panier_session = request.session.get('id_panier_session', None)

				if id_panier_session:
					maj_session(id_session=id_panier_session, panier=panier)
				# Calcul du montant de la commande
				montant=0.0
				for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
					montant += pp.quantite*pp.produit.prix

			except Exception as e:
				return render(request, "Errors/500.html", status=500)
			else:
				# Creation de la commande

				try:
					code = random.randrange(1000000,9999999)
					existance = False

					def creation_code_commande():
						global code
						global existance
						for cmd in models.Commande.objects.all():
							code = random.randrange(1000000, 9999999)
							if cmd.code == code:
								existance = True
								break

					while existance == True:
						creation_code_commande()


					commande = models.Commande.objects.create(
						panier = panier,
						montant=montant,
						code = code)

					for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
						# if not pp.commande:
						pp.commande = commande
						
						if pp.produit.quantite >= pp.quantite:
							pp.produit.quantite -= pp.quantite
							pp.produit.save()
						pp.save()

				except Exception as e:
					return render(request, "Errors/500.html", status=500)
				else:
					# Creation de la livraison
					try:
						adresse_livraison = request.POST.get('adresse_livraison')
						if adresse_livraison == "abidjan":
							promo = date(2021, 10, 30) - date.today()

							if promo.days >= 0:
								livraison = models.Livraison.objects.create(
									commande=commande,
									adresse_livraison = adresse_livraison,
									frais=0.0,
									date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+1),
									status = 'en_cours'
									)
							else:
								livraison = models.Livraison.objects.create(
									commande=commande,
									adresse_livraison = adresse_livraison,
									frais=1500.0,
									date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+1),
									status = 'en_cours'
									)
						else:
							livraison = models.Livraison.objects.create(
								commande=commande,
								adresse_livraison = adresse_livraison,
								frais=2000.0,
								date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+2),
								status = 'en_cours'
								)
					except Exception as e:
						return render(request, "Errors/500.html", status=500)
					else:
						# Creation du paiement
						try:
							montant_total = montant+livraison.frais
							paiement = models.Paiement.objects.create(
								commande=commande,
								montant_total=montant_total,
								status='en_cours')
						except Exception as e:
							return render(request, "Errors/500.html", status=500)
						else:
							try:

								for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
									models.Historique.objects.create(

										num_cmd = commande.pk,
										montant_cmd = montant,
										code_cmd = code,
										
										libelle = pp.produit.libelle,
										categorie = pp.produit.categorie.nom,
										prix_vendeur = pp.produit.prix_vendeur,
										prix = pp.produit.prix,
										quantite = pp.quantite,

										frais_livraison = livraison.frais,
										adresse_livraison = livraison.adresse_livraison,

										moyen_paiement = paiement.moyen_paiement,
										montant_total = paiement.montant_total,

										client = client.user.username,
										vendeur = pp.produit.vendeur.user.username,
										)
									pp.status=1
									pp.save()
							except Exception as e:
								# paiement.delete()
								# livraison.delete()
								commande.delete()
								return render(request, "Errors/500.html", status=500)
							else:
								try:
									message = f"Une commande vient d'être passé par le client : {request.user}\nMontant: {paiement.montant_total}"
									send_mail(

										"Passation de commande.",
										message,
										"baradjis.eshop@gmail.com",
										["baradjis.eshop@gmail.com"],
										fail_silently = False
										)

									message_retour = f"Votre commande à bien été réçu.\nVous serez contacter pour la confirmation.\nMontant: {paiement.montant_total}\nMerci d\'avoir choisi baradjise-shop pour vos achats."
									send_mail(
										"Commande réçu",
										message,
										"baradjis.eshop@gmail.com",
										[client.user.email],
										fail_silently=False
										)
								except Exception as e:
									return redirect('mes_commandes', "Commande enregistré. \nVous serez contacté pour la confirmation")
								else:
									return redirect('mes_commandes', "Commande enregistré. \nVous serez contacté pour la confirmation")
	
#Gestion de la recherche 

class Recherche:

	def trier_produits(request, vue=None, requete=None, **kwargs):

		def retourner_context(paginator, produits):

			context = {
					'produits':produits,
					'nbre_produits': len(produits),
					'paginator': paginator
					}
			return context

		def pagination(produits, taille=60):

			paginator = Paginator(produits, taille)
			nombre_page = request.GET.get('page')
			page_obj = paginator.get_page(nombre_page)

			return paginator, page_obj

		render_template = "resultat_recherche_grid.html"

		if vue is not None:
			if vue == 'list':
				cache.set('vue', 'list')
				render_template = "resultat_recherche.html"
		else:
			if cache.get('vue'):
				vue = cache.get('vue')
			else:
				cache.set('vue', 'grid')
				vue = cache.get('vue')

			if vue == 'list':
				render_template = "resultat_recherche.html"

		produits = models.Produit.objects.all().exclude(Q(status=0) | Q(quantite=0))
		if request.method == 'POST':

			if request.POST.get('prix_min'):
				produits = produits.filter(Q(prix__gte=int(request.POST.get('prix_min'))))

			if request.POST.get('prix_max'):
				produits = produits.filter(Q(prix__lte=int(request.POST.get('prix_max'))))

			produits = produits.exclude(Q(status=0) | Q(quantite=0))
			
			if requete is not None:

				paginator, produits = pagination(produits)
				context = retourner_context(paginator, produits)
				context['prix_min'] = request.POST.get('prix_min')
				context['prix_max'] = request.POST.get('prix_max')
				context['requete'] = requete

				try:
					categorie = models.Categorie.objects.get(cle=requete)
				except Exception as e:
					produits = produits.filter(Q(libelle__icontains=requete))
					context['produits'] = list(produits)
					# random.shuffle(produits)

					return render(request, render_template, context)
				else:
					produits = produits.filter(categorie=categorie)
					context['produits'] = list(produits)
					random.shuffle(produits)

					# paginator, produits = pagination(produits)

					try:
						message = kwargs['message']
					except KeyError as e:
						return render(request, render_template, context)
					else:
						context['message_success'] = message
						return render(request, render_template, context)

			produits = list(produits)
			random.shuffle(produits)

			paginator, produits = pagination(produits)
			context = retourner_context(paginator, produits)
			context['prix_min'] = request.POST.get('prix_min')
			context['prix_max'] = request.POST.get('prix_max')

			try:
				message = kwargs['message']
			except KeyError as e:
				return render(request, render_template, context)
			else:
				context['message_success'] = message
				return render(request, render_template, context)

		else:
			paginator, produits = pagination(produits)
			context = retourner_context(paginator, produits)

			try:
				message = kwargs['message']
			except Exception as e:
				pass
			else:
				context['message_success'] = message
			if requete is not None:

				context['requete'] = requete
				try:
					categorie = models.Categorie.objects.get(cle=requete)
					produits = produits.filter(categorie=categorie).exclude(Q(status=0) | Q(quantite=0))
					context['produits'] = list(produits)
					random.shuffle(context['produits'])
				except:
					context['produits'] = list(produits.filter(Q(libelle__icontains=requete)))
					random.shuffle(context['produits'])

					# context['paginator'], context['produits'] = pagination(produits)
					return render(request, render_template, context)
				else:
					# context['paginator'], context['produits'] = pagination(produits)
					return render(request, render_template,  context)

			context['produits'] = list(produits)
			random.shuffle(context['produits'])

			# context['paginator'], context['produits'] = pagination(produits)
			return render(request, render_template, context)

	# Methode a utilise pour la barre de recherche
	def barre_recherche(request, **kwargs):

		if request.method == 'POST':
			form = request.POST
			produits = models.Produit.objects.filter(Q(libelle__icontains=form.get('requete'))).exclude(Q(status=0) | Q(quantite=0))
			produits = list(produits)
			random.shuffle(produits)

			paginator = Paginator(produits, 60)
			nombre_page = request.GET.get('page')
			produits = paginator.get_page(nombre_page)
			return render(request, "resultat_recherche_grid.html", {
				'produits': produits,
				'nbre_produits': len(produits),
				'requete': form.get('requete'),
				'paginator': paginator
				})


		else:
			return redirect('trier_produits')

	# methode de recherche de categorie
	def rechercher_categorie(request, categorie, **kwargs):

		try:
			categorie = models.Categorie.objects.get(cle=categorie)
		except Exception as e:
			return redirect('trier_produits')
		else:
			return redirect('trier_produits', None, categorie.cle)

	# Methode permettant de rendre la boutique du vendeur
	def rechercher_boutique(request, vendeur, **kwargs):

		try:
			user = User.objects.get(username=vendeur)
			vendeur = models.Vendeur.objects.get(user=user)	
		except Exception as e:
			raise Http404()
		else:
			try:
				produits = models.Produit.objects.filter(vendeur=vendeur).exclude(status=0)
			except Exception as e:
				raise e
			else:
				try:
					produits = list(produits)
					# produits = random.sample(produits, len(produits))
					random.shuffle(produits)

					paginator = Paginator(produits, 60)
					nombre_page = request.GET.get('page')
					page_obj = paginator.get_page(nombre_page)
				except Exception as e:
					raise e
				else:
					context = {
						'produits': page_obj,
						'vendeur': vendeur,
						'nbre_produits':len(produits),
						'paginator': paginator,
						}
					try:
						message = kwargs['message']
					except Exception as e:

						return render(request, "boutique_vendeur.html", context)
					else:
						context['message_success'] = kwargs['message']
						return render(request, "boutique_vendeur.html", context)

	#Recherches en fonction du budget
	# def fonc_budget(request, boutique):

	# 	liste = ['Sidiberashop', 'Driptown', 'RO-BOUTIQUE', 'Mr-le-boss']
	# 	produits = models.Produit.objects.all().exclude(Q(status=0) | Q(quantite=0))
	# 	if boutique == 'luxe':
	# 		try:

	# 			v1 = models.Vendeur.objects.get(user=User.objects.get(username=liste[0]))
	# 			v2 = models.Vendeur.objects.get(user=User.objects.get(username=liste[1]))
	# 			v3 = models.Vendeur.objects.get(user=User.objects.get(username=liste[2]))
	# 			v4 = models.Vendeur.objects.get(user=User.objects.get(username=liste[3]))
	# 			produits = produits.filter(Q(vendeur=v1) | Q(vendeur=v2) | Q(vendeur=v3) | Q(vendeur=v4))

	# 			produits = list(produits)
	# 			# produits = random.sample(produits, len(produits))
	# 			random.shuffle(produits)

	# 			paginator = Paginator(produits, 60)
	# 			nombre_page = request.GET.get('page')
	# 			produits = paginator.get_page(nombre_page)
	# 		except Exception as e:
	# 			raise e
	# 		else:
	# 			return render(request, "resultat_recherche_grid.html", {
	# 				'produits': produits,
	# 				'nbre_produits': len(produits),
	# 				'paginator': paginator
	# 				})
	# 	elif boutique == 'cheap':
	# 		try:
	# 			for l in liste:
	# 				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=l))
	# 				produits = produits.exclude(vendeur=vendeur)

	# 			produits = list(produits)
	# 			# produits = random.sample(produits, len(produits))
	# 			random.shuffle(produits)

	# 			paginator = Paginator(produits, 60)
	# 			nombre_page = request.GET.get('page')
	# 			produits = paginator.get_page(nombre_page)
	# 		except Exception as e:
	# 			raise e
	# 		else:
	# 			return render(request, "resultat_recherche_grid.html", {
	# 				'produits': produits,
	# 				'nbre_produits': len(produits),
	# 				'paginator': paginator
	# 				})
	# 	else:
	# 		return redirect('trier_produits')


	# methode de renvois de tous les produits
	def tous_les_produits(request):

		produits = models.Produit.objects.all().exclude(Q(status=0) | Q(quantite=0))

		produits = list(produits)
		random.shuffle(produits)

		paginator = Paginator(produits, 20)
		nombre_page = request.GET.get('page')
		produits = paginator.get_page(nombre_page)
		return render(request, "resultat_recherche_grid.html",{
			'produits': produits,
			'nbre_produits': len(produits),
			'paginator': paginator
			})


@login_required(login_url="/authentification/")
def dashboard_client(request):

	try:
		user = User.objects.get(username=request.user)
		client = models.User.objects.get(user=request.user)
	except Exception as e:
		return redirect("authentification")
	else:
		try:
			panier = models.Panier.objects.get(user=client)
			nbre_cmd = 0
			att_livr = 0
			livree = 0
			nbre_produit_panier = 0
			num_cmd = []
			for his in models.Historique.objects.filter(client=user.username):
				if not his.num_cmd in num_cmd:
					nbre_cmd+=1
					num_cmd.append(his.num_cmd)
				if his.status_livraison == 'en_cours':
					att_livr +=1
				if his.status_livraison == 'faite':
					livree +=1
			for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
				nbre_produit_panier += 1

			nbre_souhait = 0
			for souhait in client.produituser_set.all():
				nbre_souhait+=1

		except Exception as e:
			return render(request, "Errors/500.html", status=500)
		else:
			return render(request, "Client/dashboard.html", {
				'client': client, 
				'nbre_cmd': nbre_cmd, 
				'nbre_souhait':nbre_souhait, 
				'att_livr': att_livr, 
				'livree': livree, 
				'nbre_produit_panier':nbre_produit_panier,
				'active':"dashboard"})


# Page d'accueil
def accueil(request, **kwargs):

	print("kwargs :", kwargs)
	try:
		produits = models.Produit.objects.filter(status=1).exclude(quantite=0)
		produits = list(produits)

		produits = random.sample(produits, len(produits))
		i=0
		produits_temp = []
		for produit in produits:
			if i == 12:
				break
			else:
				produits_temp.append(produits[i])
				i+=1
	except Exception as e:
		return render(request, "Errors/500.html", status=500)
	else:

		try:
			message = kwargs['message']
		except KeyError as e:
			return render(request, "accueil.html", {'produits':produits_temp, 'requete': None})
			# raise e
		else:
			return render(request, "accueil.html", {'produits':produits_temp, 'requete': None, 'message_success': message})
			
		# if kwargs['message']:

# Commandes passees par les clients
@login_required(login_url="/authentification/")
def mes_commandes(request, message=None):

	try:
		client = models.User.objects.get(user=request.user)
	except Exception as e:
		return redirect("authentification")
	else:
		try:
			historiques = models.Historique.objects.filter(client=request.user).order_by("-date_cmd")
		except Exception as e:
			return render(request, "Errors/500.html", status=500)
		else:
			return render(request, "Client/mes_commandes.html", {
						'historiques': historiques,
						'message_success': message,
						'active':"commande"})

# Detail du produit
def detail_produit(request, id_produit):

	try:
		produit = models.Produit.objects.get(pk=id_produit)
	except Exception as e:
		raise Http404()
	else:
		return render(request, "Client/detail_produit.html", {'produit':produit})

class Envie:

	# @login_required(login_url="/authentification/")
	def ajouter(request, id_produit):

		if request.GET.get('vendeur'):
			kwargs = {'vendeur': request.GET.get('vendeur')}
		else:
			kwargs = dict()

		redirect_to = request.GET.get('next')
		redirect_to = resolve(redirect_to).url_name
		print(redirect_to)
		try:
			produit = models.Produit.objects.get(pk=id_produit, status=1)
		except Exception as e:
			raise Http404()
		else:
			if not request.user.is_authenticated:
				
				id_envie_session = request.session.get('id_envie_session', None)

				if id_envie_session:
					try:
						envie = models.Envie.objects.get(id = id_envie_session)
					except Exception as e:
						raise e
					else:
						try:
							models.EnvieProduit.objects.get(envie = envie, produit = produit)
						except Exception as e:
							models.EnvieProduit.objects.create(
								envie=envie,
								produit=produit
							)
							kwargs['message'] = "Produit ajouté aux envies"
							return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))

				else:
					envie = models.Envie.objects.create()
					request.session['id_envie_session'] = envie.id
					try:
						models.EnvieProduit.objects.get(envie = envie, produit = produit)
					except Exception as e:
						models.EnvieProduit.objects.create(
							envie=envie,
							produit=produit
						)
						kwargs['message'] = "Produit ajouté aux envies"
						return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))
				kwargs['message'] = "Ce produit existe deja dans vos envies."
				return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))
			else:
				try:
					client = models.User.objects.get(user=request.user)
					envie = models.Envie.objects.get(user=client)
				except Exception as e:
					return redirect('authentification')
				else:
					try:
						envie_produit =  models.EnvieProduit.objects.get(produit=produit, envie=envie)
					except Exception as e:
						envie_produit = models.EnvieProduit.objects.create(produit=produit, envie=envie)

						kwargs['message'] = "Produit ajouté aux envies"
						return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))
					else:

						kwargs['message'] = "Cet article existe deja dans vos envies."
						return HttpResponseRedirect(reverse(redirect_to, kwargs=kwargs))

	# @login_required(login_url="/authentification/")
	def lister(request, message=None):

		id_envie_session = request.session.get('id_envie_session', None)

		if not request.user.is_authenticated:
			if id_envie_session:
				try:
					envie = models.Envie.objects.get(id = id_envie_session)
				except Exception as e:
					raise e
			else:
				envie = models.Envie.objects.create()

			envie_produit = models.EnvieProduit.objects.filter(envie=envie)

		else:
			try:
				client = models.User.objects.get(user=request.user)
				envie = models.Envie.objects.get(user=client)
			except Exception as e:
				return render(request, "Errors/500.html", status=500)
			else:
				if id_envie_session:
					maj_session(id_session=id_envie_session, envie = envie)
				envie_produit = models.EnvieProduit.objects.filter(envie=envie)

		try:

			for ep in envie_produit:
				if ep.produit.quantite <= 0:
					envie_produit = envie_produit.exclude(produit=ep.produit)
		except Exception as e:
			return render(request, "Errors/500.html", status=500)
		else:
			return render(request, "Client/mes_envies.html", {
				'envie_produit':envie_produit, 
				'message_success': message,
				'active':"souhait"})

	# @login_required(login_url="/authentification/")
	def supprimer(request, id_envie_produit):

		if not request.user.is_authenticated:
			id_envie_session = request.session.get('id_envie_session', None)
			envie = models.Envie.objects.get(id = id_envie_session)

			try:
				envie_produit = models.EnvieProduit.objects.get(
					id = id_envie_produit,
					envie = envie,
				)
			except Exception as e:
				raise e
			else:
				envie_produit.delete()
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return render(request, "Errors/500.html", status=500)
			else:
				try:
					envie_produit = models.EnvieProduit.objects.get(pk=id_envie_produit)
				except Exception as e:
					raise Http404()
				else:
					envie_produit.delete()

		return redirect('lister_envie', "L'article à bien été supprimé")

class Compte:

	# Changer les informations sur un utilisateur
	@login_required(login_url="/authentification/")
	def changer_infos_user(request):

		try:
			client = models.User.objects.get(user=request.user)
		except Exception as e:
			return render(request, "Errors/500.html", status=500)
		else:
			if request.method == 'POST':
				form = request.POST

				try:
					if form.get('mdp'):
						client.user.set_password(form.get('mdp'))
					if form.get('email'):
						client.user.email = form.get('email')
					if form.get('adresse'):
						client.adresse = form.get('adresse')
					client.user.save()
					client.save()
				except Exception as e:
					return render(request, "Errors/500.html", status=500)
				else:
					logout(request)
					return render(request, "Client/authentification.html", {
							'user':client, 'message_success': "Les infos ont ete mis à jour. Vous devez vous reconnecter."})
			else:
				return render(request, "Client/changer_infos_user.html", {'user':client, 'active': "parametre"})

	@login_required(login_url="/authentification/")
	def changer_profil_user(request):

		try:
			client = models.User.objects.get(user=request.user)
		except Exception as e:
			return redirect('authentification', "Veuillez vous authentifier d\'abord")
		else:
			if request.method == 'POST':

				form_profil = request.FILES
				try:
					chemin_firebase = f"Profils Clients/{request.user}/{form_profil.get('profil')}"
					chemin = storage.child(chemin_firebase).put(form_profil.get('profil'))
					client.profil = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])
					client.save()
				except Exception as e:
					return render(request, "Errors/500.html", status=500)
				else:
					return render(request, "Client/changer_infos_user.html", {
						'user': client, 'message_success': "Votre profil a ete mis a jour",
						'active':"parametre"})
			else:
				return render(request, "Client/changer_infos_user.html", {
					'user': client,
					'active': "parametre"})

# Gestion des vendeurs
class Vendeur:

	# Le systeme d'authentification ne se fait pas avec Firebase mais avec celui de django

	def inscription(request):

		if request.method == 'POST':

			form = request.POST

			# Tentative de reccuperation du vendeur dans la table auth_user. Pour voir s'il n'est pas encore enregistre
			try:
				# Gag, je venais de decouvrir la classe Q, il fallait la tester.
				user = User.objects.get(Q(username=form.get('username')))
			except Exception as e:
				# S'il ne l'est pas on l'enregistre dans auth_user
				try:
					user = User.objects.create_user(
						username=form.get('username'), 
						password=form.get('mdp'),
						last_name=form.get('nom'))
				except Exception as e:
					return render(request, "Vendeur/inscription.html", {
						'message': "Erreur lors de la création du compte. Si le problème persiste,"
									"veuillez nous contacter au 0556748529",
						'form': form
						})
				else:
					# On cree le vendeur associe
					try:
						vendeur = models.Vendeur.objects.create(
							adresse = form.get('adresse'),
							user = user)
					except Exception as e:
						user.delete()
						return render(request, "Vendeur/inscription.html", {
						'message': "Erreur lors de la création du compte. Si le problème persiste,"
									"veuillez nous contacter au 0556748529",
						'form': form
						})
					else:
						try:
							message = f("Un nouveau compte vendeur vient d'être crée.\n"
										"Nom : {form.get('nom')}\nContact : {form.get('contact1')}"
										)
							send_mail(

								"Création d'un compte vendeur.",
								message,
								form.get('email'),
								["baradjis.eshop@gmail.com"],
								fail_silently = False
								)
						except Exception as e:
							return render(request, "Vendeur/authentification.html", {
								'message_success': "Votre compte a été enregistrer.",
								'form': form
								})
						else:
							return render(request, "Vendeur/authentification.html", {
								'message_success': "Votre compte a été enregistrer."
								})
			else:
				return redirect('authentification_vendeur', ("Un compte associé à ce numéro de téléphone existe déja."
																"Contactez-nous pour plus d'infos"))

		else:
			return render(request, "Vendeur/inscription.html")


	def authentification(request, message=None):

		if request.method == 'POST':

			form = request.POST
			# authenticate renvoi None si le auth_user n'existe pas et le champ de auth_user sinon
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=form.get('username')))
			except Exception as e:
				return render(request, "Vendeur/authentification.html", {
					'message': "Compte inexistant",
					'message_infos':message })
			else:
				user = authenticate(username=form.get('username'), password=form.get('mdp'))
				if user is not None:
					login(request, user)
					return redirect('dashboard_vendeur')
					# return HttpResponseRedirect(form.get('suivant'))
				else:
					contexte = {'message': "Nom d'utilisateur ou mot de passe incorrect."}
					return render(request,"Vendeur/authentification.html", contexte)

		else:
			return render(request, "Vendeur/authentification.html",{
							'message_infos': "Veuillez vous authentifier dabord", 
							})

	# De parler? Tchrrr
	def deconnexion(request):

		logout(request)
		return render(request, "Vendeur/authentification.html", {'message_success':"Déconnexion réussie"})

	def dashboard(request):
		# Verification s'il est authentifie
		if request.user.is_authenticated:
			# On reccupere le vendeur et ses produits.
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=request.user))
			except:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:

				try:
					nbre_produits = 0
					nbre_art_actif = 0
					nbre_art_vendu = 0

					for produit in models.Produit.objects.filter(vendeur=vendeur):
						nbre_produits += 1

						if produit.status == True:
							nbre_art_actif += 1

					for his in models.Historique.objects.filter(vendeur=vendeur.user.username):
						nbre_art_vendu += 1
				except Exception as e:
					return render(request, "Errors/500.html", status=500)
				else:
					return render(request, "Vendeur/dashboard.html", {
						'vendeur': vendeur,
						'nbre_produits': nbre_produits,
						'nbre_art_actif': nbre_art_actif,
						'nbre_art_vendu': nbre_art_vendu,
						'active': "dashboard_vendeur"})
		else:
			return redirect('authentification_vendeur')

	def liste_produit(request, message_success=None):

		if request.user.is_authenticated:
			# On reccupere le vendeur et ses produits.
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=request.user))
			except:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:

				if request.method == 'POST':
					produits =models.Produit.objects.filter(
						Q(vendeur=vendeur)&
						Q(libelle__icontains = request.POST.get('requete'))
						).order_by("date_ajout")
				else:
					produits = models.Produit.objects.filter(vendeur=vendeur).order_by("-date_ajout")

					for p in produits:
						if p.quantite <= 0:
							p.status = False
							p.save()
					
				produits = list(produits)
				# produits = random.sample(produits, len(produits))

				paginator = Paginator(produits, 12)
				nombre_page = request.GET.get('page')
				page_obj = paginator.get_page(nombre_page)
				return render(request, "Vendeur/liste_produits.html",{
					'produits': page_obj,
					'active': "liste_produits_vendeur",
					'nbre_produits': len(produits),
					'message_success':message_success,
					'paginator': paginator
					})

		else:
			return redirect('authentification_vendeur')

	def ajouter_produit(request):

		if request.user.is_authenticated:

			if request.method == 'POST':

				form = request.POST
				form_images = request.FILES.getlist('images')
				try:
					vendeur = models.Vendeur.objects.get(user=request.user)
				except Exception as e:
					return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
				else:
					try:
						categorie = models.Categorie.objects.get(cle=form.get('categorie'))
					except Exception as e:
						return render(request, "Vendeur/ajouter_produit.html", {
							'message':"Veuillez choisir une catégorie",
							'form': form,
							'categories': models.Categorie.objects.all(),

							})
					else:
						try:

							prix = int(form.get('prix_vendeur'))*(1+ categorie.commission/100.0)
							prix = int(prix)
							produit = models.Produit.objects.create(
								libelle = form.get('libelle'),
								categorie = categorie,
								description = form.get('description'),
								prix_vendeur = form.get('prix_vendeur'),
								prix = prix,
								quantite =form.get('quantite'),
								status = True,
								vendeur = vendeur,
								)	

							# Enregistrement de l'image qui sera vue en premiere position
							chemin_firebase = f"Produits/{request.user}/{form_images[0]}"
							chemin = storage.child(chemin_firebase).put(form_images[0])
							image = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])

							produit.image = image
							produit.save()
							del form_images[0]
							

							# Enregistrement des autres images
							if len(form_images) > 0:

								for img in form_images:
									chemin_firebase = f"ProduitsImagesSup/{request.user}/{img}"
									chemin = storage.child(chemin_firebase).put(img)
									image = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])

									models.ImageProduit.objects.create(produit=produit, image=image)

						except Exception as e:
							return render(request, "Vendeur/ajouter_produit.html", {
								'message':"Erreur lors de l\'ajout de produit. Si le problème persiste veuillez nous contacter au 0556748529",
								'form': form,
								'categories': models.Categorie.objects.all(),

								})
							# raise e
						else:
							return redirect('liste_produits_vendeur', message_success="Ajout éffectué avec succès")

			else:
				return render(request, "Vendeur/ajouter_produit.html", {
					'categories': models.Categorie.objects.all(),
					'active': "ajouter_produit_vendeur"})

		else:
			return redirect('authentification_vendeur')

	def supprimer_produit(request, id_produit):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				try:
					produit_a_supprimer = models.Produit.objects.get(pk = id_produit, vendeur = vendeur)
				except Exception as e:
					raise Http404()
				else:
					produit_a_supprimer.status = 0
					produit_a_supprimer.delete()
					return redirect('liste_produits_vendeur', "Produit supprimé")

		else:
			return redirect('authentification_vendeur')

	def modifier_produit(request, id_produit):

		if request.user.is_authenticated:

			if request.method == 'POST':
				form = request.POST
				form_image = request.FILES
				try:
					vendeur = models.Vendeur.objects.get(user=request.user)
				except Exception as e:
					return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
				else:
					try:
						produit_a_modifier = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)
						categories = models.Categorie.objects.all()
					except Exception as e:
						raise Http404()
					else:
						try:
							categorie = models.Categorie.objects.get(cle=form.get('categorie'))
						except Exception as e:
							return render(request, "Vendeur/modifier_produit.html",{
								'produit': produit_a_modifier,
								'categories': categories,
								'message': "Veuillez choisir une catégorie."
								})
						else:
							try:
								prix = int(form.get('prix_vendeur'))*(1+ categorie.commission/100.0)
								# prix = int(prix)
								produit_a_modifier.libelle = form.get('libelle')
								produit_a_modifier.categorie = categorie
								produit_a_modifier.prix_vendeur = form.get('prix_vendeur')
								produit_a_modifier.prix = prix
								produit_a_modifier.description = form.get('description')
								produit_a_modifier.quantite = form.get('quantite')

								# On modifie la visibilite du produit par les clients
								if form.get('status') == 'on' or form.get('status') == True:
									produit_a_modifier.status = 1
								else:
									produit_a_modifier.status = 0

								if form_image.get('image'):
									try:
										chemin_firebase = f"Produits/{request.user}/{form_image.get('image')}"
										chemin = storage.child(chemin_firebase).put(form_image.get('image'))
										image = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])
									except Exception as e:
										return render(request, "Vendeur/modifier_produit.html",{
											'form': form,
											'categories': categories,
											'message': "Erreur lors de l'enregistrement de l'image."
											})
									else:
										produit_a_modifier.image = image

							except Exception as e:
								return render(request, "Vendeur/modifier_produit.html", {
									'produit': produit_a_modifier, 
									'categories':categories,
									'message': "Erreur lors de la mis à jour du produit"
									})
							else:
								produit_a_modifier.save()
								return redirect("liste_produits_vendeur", "Produit modifié")
			else:
				# On aura besoin des categories dans le template pour le choix de la categorie
				categories = models.Categorie.objects.all()
				user = User.objects.get(username=request.user)
				produit = models.Produit.objects.get(pk = id_produit, vendeur=models.Vendeur.objects.get(user=user))
				return render(request, "Vendeur/modifier_produit.html", {'produit': produit, 'categories':categories})
		else:
			return redirect('authentification_vendeur')

	# Definir si le produit peut etre vue ou non par l'utilisateur
	def changer_status_produit(request, id_produit):


		if request.user.is_authenticated:

			if request.method == 'POST':

				try:
					vendeur = models.Vendeur.objects.get(user=request.user)

				except Exception as e:
					return redirect('authentification_vendeur',"Veuillez vous authentifier d\'abord")
				else:
					try:
						produit_a_modifier = models.Produit.objects.get(pk= id_produit, vendeur=vendeur)
					except Exception as e:
						raise Http404()
					else:
						if request.POST.get('status') is not None:
							produit_a_modifier.status = True
						else:
							produit_a_modifier.status = False
						produit_a_modifier.save()

						return redirect('dashboard_vendeur')

			else:
				return redirect('dashboard_vendeur')
		else:
			return redirect('authentification_vendeur')

	def detail_produit(request, id_produit):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				try:
					produit = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)
					image_produit = models.ImageProduit.objects.filter(produit=produit)
				except Exception as e:
					raise Http404()
				else:
					return render(request, "Vendeur/detail_produit.html", {
						'produit': produit, 
						'image_produit':image_produit,})

		else:
			return redirect('authentification_vendeur')

	# Ajouter une image supplementaire a un produit
	def ajouter_image_produit(request, id_produit):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:

				try:
					form_images = request.FILES.getlist('images')
					produit = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)

					for img in form_images:
						chemin_firebase = f"ProduitsImagesSup/{request.user}/{img}"
						chemin = storage.child(chemin_firebase).put(img)
						image = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])

						models.ImageProduit.objects.create(produit=produit, image=image)
				except Exception as e:
					return redirect('detail_produit_vendeur', id_produit)
				else:
					return redirect('detail_produit_vendeur', id_produit)

		else:
			return redirect('authentification_vendeur')

	def supprimer_image_produit(request, id_image):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				try:
					image_produit_a_supprimer = models.ImageProduit.objects.get(pk=id_image)
					produit = models.Produit.objects.get(vendeur=vendeur, imageproduit=image_produit_a_supprimer)
				except Exception as e:
					return redirect('dashboard_vendeur')
				else:
					image_produit_a_supprimer.delete()
					return redirect('detail_produit_vendeur', produit.pk)

		else:
			return redirect('authentification_vendeur')

	def modifier_infos_vendeur(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				if request.method == 'POST':

					form = request.POST

					try:
						if form.get('mdp'):
							vendeur.user.set_password(form.get('mdp'))
						if form.get('email'):
							vendeur.user.email = form.get('email')
						if form.get('adresse'):
							vendeur.adresse = form.get('adresse')
						if form.get('produits_vendu'):
							vendeur.produits_vendu = form.get('produits_vendu')
					except Exception as e:
						return  render(request, "Vendeur/modifier_infos_vendeur.html", {
							'vendeur': vendeur, 
							'active':"parametres", 
							'message': "Erreur lors de la modification. Si le problème persiste veuillez nous contacter."})
					else:
						vendeur.user.save()
						vendeur.save()
						logout(request)
						return render(request, "Vendeur/authentification.html", {
							'message_success': "Vos modifications ont été prises en compte. Veuillez vous reconnecter"
							})
						
				else:
					return render(request, "Vendeur/modifier_infos_vendeur.html", {
						'vendeur': vendeur, 
						'active':"parametres"})
		else:
			return redirect('authentification_vendeur')

	def changer_profil_vendeur(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				if request.method == 'POST':

					form_profil = request.FILES
					
					try:
						chemin_firebase = f"Profils Vendeurs/{request.user}/{form_profil.get('profil')}"
						chemin = storage.child(chemin_firebase).put(form_profil.get('profil'))
						vendeur.profil = storage.child(chemin_firebase).get_url(chemin['downloadTokens'])
						vendeur.save()
					except Exception as e:
						return render(request, "Vendeur/modifier_infos_vendeur.html", {
							'vendeur': vendeur, 
							'message': "Erreur lors de la modification du profil. Si le problème persiste veuillez nous contacter",
							'active':"parametres"})
					else:
						return render(request, "Vendeur/modifier_infos_vendeur.html", {
							'vendeur': vendeur, 
							'message_success': "Votre profil a été mis a jour",
							'active':"parametres"})
				else:
					return render(request, "Vendeur/modifier_infos_vendeur.html", {
						'vendeur': vendeur,
						'active': "parametres"})
		else:
			return redirect('authentification_vendeur')

	# Chaque vendeur a dans son dashboard, l'historique de ses ventes
	def historique_paiement(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur', "Veuillez vous authentifier d\'abord")
			else:
				historiques = models.Historique.objects.filter(vendeur = request.user)
				return render(request, "Vendeur/historique_paiement.html", {
					'historiques': historiques,
					'active': "historique_paiement_vendeur"})
		else:
			return redirect('authentification_vendeur')

def mot_de_passe_oublie(request):

	if request.method == 'POST':
		form = request.POST
		try:
			user = User.objects.get(username=form.get('username'), email=form.get('email'))
		except Exception as e:
			return render(request, "mot_de_passe_oublie.html", {'message': "Cet utilisateur n'existe pas."})
		else:
			if form.get('mdp') == form.get('c_mdp'):

				if len(form.get('mdp')) >= 6:
					user.set_password(form.get('mdp'))
					user.save()
					try:
						vendeur = models.Vendeur.objects.get(user=user)
					except Exception as e:
						return render(request, "Client/authentification.html", {
							'message_success': "Votre mot de passe à été mis à jour."
							})
					else:
						return render(request, "Vendeur/authentification.html", {
							'message_success': "Votre mot de passe à été mis à jour."
							})
				else:
					return render(request, "mot_de_passe_oublie.html", {
						'message': "Le mot de passe doit contenir au moins 6 caracteres.", 
						'form': form
						})
			else:
				return render(request, "mot_de_passe_oublie.html", {
					'message': "Les mots de passe saisient ne correspondent pas", 
					'form': form})

	else:
		return render(request, "mot_de_passe_oublie.html")


def contactez_nous(request):

	if request.method == 'POST':

		form = request.POST
		try:

			message = f"Nom : {form.get('nom')}\nContact : {form.get('contact')}\nMessage : {form.get('message')}"
			send_mail(
				form.get('objet'),
				message,
				form.get('email'),
				['baradjis.eshop@gmail.com'],
				fail_silently=False
				)
		except Exception as e:
			raise e
		else:
			return render(request, "contactez-nous.html", {"message": "Votre message à bien été envoyé."})

	else:
		return render(request, "contactez-nous.html")



def handler404(request, exception):

	return render(request, "Errors/404.html",{}, status=404)

def handler500(request):

	return render(request, "Errors/500.html", status=500)


class OffreSpeciale:

	# @method_decorator(login_required, name='dispatch')
	class SpecialRamadan(View):

		template_name = "Client/special_ramadan.html"
		def get(self, request):
			offres = [95, 50, 47, 43, 40, 48, 47, 45, 43, 142, 182, 183, 184, 185, 186, 187, 188, 189]
			produits = []
			for offre in offres:

				produits.append(models.Produit.objects.get(pk=offre))

			context = {'produits': produits, 'taille': len(produits)}

			return render(request, self.template_name, context)