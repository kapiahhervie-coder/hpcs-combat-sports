from django.urls import path
from . import views

urlpatterns = [
    path("bmi-bodyfat/", views.calc_bmi_bodyfat, name="calc_bmi_bodyfat"),
    path("1rm/", views.calc_one_rep_max, name="calc_one_rep_max"),
    path("tdee/", views.calc_tdee, name="calc_tdee"),
    path("target-hr/", views.calc_target_hr, name="calc_target_hr"),
    path("vo2-12min/", views.calc_vo2_12min, name="calc_vo2_12min"),
    path("risk/", views.calc_risk, name="calc_risk"),
    path("denyut-nadi/", views.calc_denyut_nadi, name="calc_denyut_nadi"),
    path("pushup/", views.calc_pushup, name="calc_pushup"),
    path("situp/", views.calc_situp, name="calc_situp"),
    path("plank/", views.calc_plank, name="calc_plank"),
    path("squat/", views.calc_squat, name="calc_squat"),
    path("crunch/", views.calc_crunch, name="calc_crunch"),
]
