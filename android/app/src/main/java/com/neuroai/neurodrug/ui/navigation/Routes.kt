// NeuroAI Android Navigation Routes
package com.neuroai.neurodrug.ui.navigation

/**
 * Navigation routes for NeuroAI Android Application
 * 
 * Route naming convention:
 * - SCREEN_NAME: Main screen routes
 * - {paramName}: Dynamic route parameters
 */
object Routes {
    // Authentication
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val FORGOT_PASSWORD = "forgot_password"
    
    // Main Navigation
    const val DASHBOARD = "dashboard"
    const val DRUG_RECOMMENDATIONS = "drug_recommendations"
    const val DRUG_DETAIL = "drug_detail"
    const val PATHWAY_VISUALIZATION = "pathway_visualization"
    const val RISK_ASSESSMENT = "risk_assessment"
    const val PATIENT_PROFILE = "patient_profile"
    const val SETTINGS = "settings"
    
    // Data detail routes
    const val DRUG_DETAIL_ROUTE = "$DRUG_DETAIL/{drugId}"
    const val PATHWAY_DETAIL_ROUTE = "$PATHWAY_VISUALIZATION/{pathwayId}"
}

/**
 * Navigation graph constants
 */
object NavigationDefaults {
    // Animation durations (milliseconds)
    const val FADE_DURATION = 300
    const val SLIDE_DURATION = 350
    
    // Bottom navigation items
    val bottomNavItems = listOf(
        BottomNavItem("Dashboard", Routes.DASHBOARD),
        BottomNavItem("Drugs", Routes.DRUG_RECOMMENDATIONS),
        BottomNavItem("Pathways", Routes.PATHWAY_VISUALIZATION),
        BottomNavItem("Risk", Routes.RISK_ASSESSMENT),
        BottomNavItem("Profile", Routes.PATIENT_PROFILE),
    )
}

data class BottomNavItem(
    val label: String,
    val route: String,
)
