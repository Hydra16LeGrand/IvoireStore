from django.conf.urls import url, handler404
from django.urls import path
from django.conf import settings

from django.conf.urls.static import static
from . import views


urlpatterns = [
	
	path("", views.accueil, name = "accueil"),
	path("?<str:message>", views.accueil, name = "accueil"),

	# url(r'^$', views.accueil, name='accueil'),

	url(r'^inscription/$', views.Acces.inscription, name='inscription'),
	url(r'^authentification/$', views.Acces.authentification, name='authentification'),
	path('authentification/?<str:message>', views.Acces.authentification, name='authentification'),
	path('mon_compte/deconnexion/', views.Acces.deconnexion, name='deconnexion'),
	path('client/dashboard/', views.dashboard_client, name='dashboard_client'),

	path('Panier/ajouter/<int:id_produit>/', views.Panier.ajouter, name='ajouter_panier'),
	path('Panier/', views.Panier.lister, name='lister_panier'),
	path('Panier/?<str:message>/', views.Panier.lister, name='lister_panier'),
	path('Panier/modifier/<int:id_produit>/', views.Panier.modifier, name='modifier_panier'),
	path('Panier/supprimer/<int:id_produit>/', views.Panier.supprimer, name='supprimer_panier'),
	path('Panier/finaliser_commande/', views.Panier.finaliser_commande, name='finaliser_commande'),

	path('mon_compte/mes_commandes/', views.mes_commandes, name='mes_commandes'),
	path('mon_compte/mes_commandes/?<str:message>?/', views.mes_commandes, name='mes_commandes'),

	path('rechercher-categorie/<str:categorie>/', views.Recherche.rechercher_categorie, name='rechercher_categorie'),
	path('rechercher-boutique/<str:vendeur>/', views.Recherche.rechercher_boutique, name='rechercher_boutique'),
	path('rechercher-boutique/<str:vendeur>/?<str:message>/', views.Recherche.rechercher_boutique, name='rechercher_boutique'),
	path('barre-recherche/', views.Recherche.barre_recherche, name='barre_recherche'),
	path('barre-recherche/?<str:message>', views.Recherche.barre_recherche, name='barre_recherche'),
	path('tri-articles/', views.Recherche.trier_produits, name='trier_produits'),
	path('tri-articles/?<str:message>', views.Recherche.trier_produits, name='trier_produits'),
	path('tri-articles/<str:vue>/', views.Recherche.trier_produits, name='trier_produits'),
	path('tri-articles/<str:vue>/<str:requete>/', views.Recherche.trier_produits, name='trier_produits'),
	# path('fonction-budget/<str:boutique>/', views.Recherche.fonc_budget, name='fonc_budget'),
	path('articles/', views.Recherche.tous_les_produits, name='tous_les_produits'),

	path('mon_compte/changer-infos-user/', views.Compte.changer_infos_user, name='changer_infos_user'),
	path('mon_compte/changer-profil-client/', views.Compte.changer_profil_user, name='changer_profil_user'),

	path('mon_compte/ajouter_envie/<int:id_produit>/', views.Envie.ajouter, name='ajouter_envie'),
	path('mon_compte/lister_envies/', views.Envie.lister, name='lister_envie'),
	path('mon_compte/lister_envies/?<str:message>/', views.Envie.lister, name='lister_envie'),
	path('mon_compte/supprimer_envie/<int:id_envie_produit>/', views.Envie.supprimer, name='supprimer_envie'),

	path('detail_produit/<int:id_produit>/', views.detail_produit, name='detail_produit'),

	# Vendeur
	path('Vendeur/', views.Vendeur.dashboard, name='dashboard_vendeur'),
	path('Vendeur/inscription', views.Vendeur.inscription, name='inscription_vendeur'),
	path('Vendeur/authentification', views.Vendeur.authentification, name='authentification_vendeur'),
	path('Vendeur/authentification/?<str:message>', views.Vendeur.authentification, name='authentification_vendeur'),
	path('Vendeur/deconnexion', views.Vendeur.deconnexion, name='deconnexion_vendeur'),
	path('Vendeur/lister-produits/', views.Vendeur.liste_produit, name='liste_produits_vendeur'),
	path('Vendeur/lister-produits/?<str:message_success>/', views.Vendeur.liste_produit, name='liste_produits_vendeur'),
	path('Vendeur/ajouter-produit/', views.Vendeur.ajouter_produit, name='ajouter_produit_vendeur'),
	path('Vendeur/supprimer-produit/<int:id_produit>/', views.Vendeur.supprimer_produit, name='supprimer_produit_vendeur'),
	path('Vendeur/modifier-produit/<int:id_produit>/', views.Vendeur.modifier_produit, name='modifier_produit_vendeur'),
	path('Vendeur/changer-status-produit/<int:id_produit>/', views.Vendeur.changer_status_produit, name='changer_status_produit'),
	path('Vendeur/detail_produit/<int:id_produit>', views.Vendeur.detail_produit, name='detail_produit_vendeur'),
	path('Vendeur/ajouter-image-produit/<int:id_produit>', views.Vendeur.ajouter_image_produit, name='ajouter_image_produit'),
	path('Vendeur/supprimer-image-produit/<int:id_image>', views.Vendeur.supprimer_image_produit, name='supprimer_image_produit'),
	path('Vendeur/modifier-infos-vendeur/', views.Vendeur.modifier_infos_vendeur, name='modifier_infos_vendeur'),
	path('Vendeur/changer-profil-vendeur/', views.Vendeur.changer_profil_vendeur, name='changer_profil_vendeur'),
	path('Vendeur/historique-paiement/', views.Vendeur.historique_paiement, name='historique_paiement_vendeur'),

	path('mot-de-passe-oublie', views.mot_de_passe_oublie, name='mot_de_passe_oublie'),
	path('contactez-nous', views.contactez_nous, name='contactez-nous'),

	# path('offre-special-ramadan/', views.OffreSpeciale.SpecialRamadan.as_view(), name='special_ramadan'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)