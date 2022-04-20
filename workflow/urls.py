from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index_workflow"),
    path('home/', views.welcome_screen, name="main"),

    # from all the buttons in the top nav bar
    path('new-customer/', views.new_customer, name="new_customer"),
    path('new-order/', views.new_order, name="new_order"),
    path('pdf-upload', views.upload_soil_sample_result, name="pdf_upload"),
    path('order-overview/', views.order_overview, name="order_overview"),
    path('search-database/', views.search_database, name="search_database"),
    path('guide/<str:guide_name>', views.workflow_guide, name="w_guide"),
    path('guide/', views.redirect_std_guide, name="w_guide_std"),
    path('functions/', views.further_functions, name="further_functions"),

    path('order/<int:order_id>', views.order_details, name="order_details"),
    path('customer/<int:kunde_id>', views.kunde_details, name="kunde_details"),
    path('soil-sample/<int:soil_sample_id>', views.soil_sample_details, name="bodenprobe_details"),

    path('error', views.raise_error, name="fehler"),

    path('media/downloads/json/soilSamplesData.json', views.download_soil_sample_json, name="download_soil_sample_json"),
    path('media/downloads/<str:inner_folder>/<str:filename>', views.download_file, name="download_file"),

    path('pdf_upload/success_message/', views.pdf_succeed, name="pdf_successful"),
    path('add-customer-successful', views.add_customer_successful, name="add_customer_successful"),
    path('auftrag/<int:auftrags_id>/<int:success>', views.auftrag_details_success_msg, name="auftrag_details_success_msg"),
    path('customer/<int:customer_id>/<int:success>', views.kunde_details_success_msg, name="kunde_details_success_msg"),
]
