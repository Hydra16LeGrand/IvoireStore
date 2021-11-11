from django.contrib import admin
from . import models
from django.contrib.auth.models import User
# Register your models here.

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
# 	list_display = ('pk', 'username', 'email', 'first_name', 'last_name','last_login', 'is_super_user', 'is_active', 'is_staff', 'date_joined')
# 	list_display_links = ['pk', 'username']

@admin.register(models.Produit)
class ProduitAdmin(admin.ModelAdmin):
	list_display = ("pk","libelle", "prix_vendeur", "prix", "quantite", "status", "image", "vendeur")
	empty_value_display = '-empty-'
	list_editable = ["status"]

@admin.register(models.Commande)
class CommandeAdmin(admin.ModelAdmin):
	list_display = ("pk","panier", "date", "status", "montant")
	list_editable = ["status"]

@admin.register(models.Livraison)
class LivraisonAdmin(admin.ModelAdmin):
	list_display = ("pk","commande", "livreur", "adresse_livraison", "frais", "date_livraison", "status")
	list_editable = ("livreur", "status")

@admin.register(models.Livreur)
class LivreurAdmin(admin.ModelAdmin):
	list_display = ("pk","nom", "prenom", "cin", "contact", "existance")

@admin.register(models.Paiement)
class PaiementAdmin(admin.ModelAdmin):
	list_display = ("pk","commande", "moyen_paiement", "montant_total", "status")
	list_editable = ["status"]

@admin.register(models.PanierProduit)
class PanierProduitAdmin(admin.ModelAdmin):
	list_display = ("pk","panier", "produit", "commande", "quantite", "date_ajout", "date_modification", "status")
	

# @admin.register(models.Panier)
# class Panier(admin.ModelAdmin):
# 	list_display = ("user", "produit")

@admin.register(models.ProduitUser)
class ProduitUser(admin.ModelAdmin):
	list_display = ("pk","produit", "user")

@admin.register(models.Vendeur)
class Vendeur(admin.ModelAdmin):
	list_display = ("pk", "adresse", "user")
	list_display_links = ["pk","user"]

@admin.register(models.Historique)
class Historique(admin.ModelAdmin):
	list_display = ("pk","num_cmd", "code_cmd", "date_cmd","montant_cmd","libelle", "prix_vendeur", "prix", "quantite", "frais_livraison", "adresse_livraison",
		"status_livraison","livreur", "montant_total", "status_paiement", "date_paiement", "client", "vendeur")
	empty_value_display = '-vide-'
	list_display_links = ["pk","num_cmd", "montant_cmd"]
	list_editable = ("status_paiement", "status_livraison", "livreur", "date_paiement")

@admin.register(models.Categorie)
class Categorie(admin.ModelAdmin):
	list_display = ("pk","nom", "cle", "commission")
	empty_value_display = '-vide-'

@admin.register(models.User)
class User(admin.ModelAdmin):
	list_display = ("pk","user", "adresse")
	list_display_links = ["pk","user"]

@admin.register(models.Avis)
class Avis(admin.ModelAdmin):
	list_display = ("pk", "note_produits", "note_livraison", "date")


# admin.site.register(models.User)
admin.site.register(models.ImageProduit)
admin.site.site_header = "Administration de Ivoire Store"
admin.site.site_title = "Administration de Ivoire Store"
admin.site.index_title = "Site d'administration de Ivoire Store"
# admin.site.register(models.Avis)
