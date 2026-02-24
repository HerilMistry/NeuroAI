// NeuroAI Android Application
// Main entry point for the NeuroAI mobile app

package com.neuroai.neurodrug

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHost
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import dagger.hilt.android.AndroidEntryPoint
import com.neuroai.neurodrug.ui.navigation.Routes
import com.neuroai.neurodrug.ui.screens.*
import com.neuroai.neurodrug.ui.theme.NeuroAITheme

/**
 * Main entry point for NeuroAI Android Application
 * 
 * Architecture:
 * - MVVM with ViewModel and Repository pattern
 * - Jetpack Compose for UI
 * - Hilt for dependency injection
 * - Room for local data persistence
 * - Retrofit + OkHttp for API communication
 * - WorkManager for background sync
 * - TensorFlow Lite for local model inference
 * 
 * Screens:
 * 1. Splash Screen - Initial loading
 * 2. Login/Auth Screen - User authentication
 * 3. Dashboard - Overview of patient data
 * 4. Drug Recommendations - ML-generated recommendations
 * 5. Drug Detail - Detailed mechanism and risk assessment
 * 6. Pathway Visualization - Interactive pathway graphs
 * 7. Risk Assessment - Safety and adverse effect analysis
 * 8. Settings - App configuration and preferences
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NeuroAITheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    NeuroAIApp()
                }
            }
        }
    }
}

@Composable
fun NeuroAIApp() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = Routes.SPLASH,
    ) {
        composable(Routes.SPLASH) {
            SplashScreen(navController)
        }
        
        composable(Routes.LOGIN) {
            LoginScreen(navController)
        }
        
        composable(Routes.DASHBOARD) {
            DashboardScreen(navController)
        }
        
        composable(Routes.DRUG_RECOMMENDATIONS) {
            DrugRecommendationsScreen(navController)
        }
        
        composable("${Routes.DRUG_DETAIL}/{drugId}") { backStackEntry ->
            val drugId = backStackEntry.arguments?.getString("drugId") ?: ""
            DrugDetailScreen(navController, drugId)
        }
        
        composable(Routes.PATHWAY_VISUALIZATION) {
            PathwayVisualizationScreen(navController)
        }
        
        composable(Routes.RISK_ASSESSMENT) {
            RiskAssessmentScreen(navController)
        }
        
        composable(Routes.SETTINGS) {
            SettingsScreen(navController)
        }
    }
}
