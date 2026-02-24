# Android Integration: Quick Start Guide

**For Android Developers**: How to integrate the new pre-trained ML endpoints

---

## Overview

The NeuroAI backend now provides 4 REST API endpoints for drug predictions using pre-trained models. No server-side training needed - call the API and get predictions <5 seconds.

---

## API Endpoints

### 1️⃣ Binding Affinity Prediction

**Endpoint**: `POST /api/v1/predictions/binding-affinity/`

**Predicts** drug-target binding strength using GraphDTA

**Request**:
```json
{
  "molecule_smiles": "CC(C)Cc1ccc(cc1)C(C)C(O)=O",
  "target_name": "COX-1",
  "target_sequence": "MGSSDQ..." (optional)
}
```

**Response** (2-4 seconds):
```json
{
  "molecule_analysis": {
    "validity": true,
    "molecular_weight": 206.28,
    "logp": 3.75,
    "h_bond_acceptors": 2,
    "h_bond_donors": 1
  },
  "binding_affinity": {
    "target": "COX-1",
    "binding_score": 8.2,
    "confidence": "high",
    "method": "GraphDTA (pre-trained)",
    "reasoning": "Strong binding predicted based on...",
    "validated": true
  },
  "status": "success"
}
```

---

### 2️⃣ Toxicity Assessment

**Endpoint**: `POST /api/v1/predictions/toxicity/`

**Predicts** molecular toxicity using MedGemma medical reasoning

**Request**:
```json
{
  "molecule_smiles": "CC(C)Cc1ccc(cc1)C(C)C(O)=O",
  "molecule_name": "Ibuprofen"
}
```

**Response** (1-3 seconds):
```json
{
  "toxicity": {
    "molecule": "Ibuprofen",
    "toxicity_risk": "medium",
    "mechanism": "Inhibits COX enzymes affecting gastric mucosa...",
    "confidence": "medium",
    "reasoning": "Well-studied compound with identified toxicity risks..."
  },
  "status": "success",
  "model": "MedGemma-7B (medical reasoning)"
}
```

---

### 3️⃣ Comprehensive Drug Response

**Endpoint**: `POST /api/v1/predictions/drug-response/`

**Combines** binding affinity + toxicity + overall recommendation

**Request**:
```json
{
  "molecule_smiles": "CC(C)Cc1ccc(cc1)C(C)C(O)=O",
  "target_name": "COX-1",
  "target_sequence": "MGSSDQ..." (optional),
  "disease_context": "Rheumatoid Arthritis" (optional)
}
```

**Response** (4-8 seconds - combines all analyses):
```json
{
  "drug_response_prediction": {
    "molecule_analysis": {...},
    "binding_affinity": {...},
    "toxicity": {...},
    "overall_assessment": {
      "composite_score": 7.8,
      "recommendation": "Good candidate - consider optimization",
      "rationale": "Strong binding to target, moderate toxicity risk, good drug-likeness"
    }
  },
  "status": "success",
  "models_used": [
    "GraphDTA (binding affinity)",
    "MedGemma-7B (toxicity, reasoning)",
    "ESM-2 (protein embeddings)",
    "RDKit (molecular features)"
  ]
}
```

---

### 4️⃣ Quick Molecule Analysis

**Endpoint**: `POST /api/v1/predictions/molecule-analysis/`

**Fast analysis** (<50ms) - just molecular properties, NO binding/toxicity

**Request**:
```json
{
  "molecule_smiles": "CCO"
}
```

**Response** (instant):
```json
{
  "analysis": {
    "smiles": "CCO",
    "validity": true,
    "molecular_weight": 46.04,
    "logp": 0.31,
    "h_bond_acceptors": 1,
    "h_bond_donors": 1
  },
  "status": "success"
}
```

---

## Android Implementation Examples

### Kotlin Implementation

```kotlin
// APIClient.kt
import com.google.gson.Gson
import okhttp3.OkHttpClient
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class NeuroAIClient(
    private val apiUrl: String = "https://api.neuroxai.com/v1",
    private val authToken: String
) {
    private val client = OkHttpClient()
    private val gson = Gson()
    
    data class BindingRequest(
        val molecule_smiles: String,
        val target_name: String,
        val target_sequence: String? = null
    )
    
    data class BindingResponse(
        val molecule_analysis: MoleculeAnalysis,
        val binding_affinity: BindingAffinity,
        val status: String
    )
    
    data class MoleculeAnalysis(
        val validity: Boolean,
        val molecular_weight: Double,
        val logp: Double,
        val h_bond_acceptors: Int,
        val h_bond_donors: Int
    )
    
    data class BindingAffinity(
        val target: String,
        val binding_score: Double,
        val confidence: String,
        val method: String,
        val reasoning: String?,
        val validated: Boolean
    )
    
    suspend fun predictBindingAffinity(
        smiles: String,
        targetName: String
    ): Result<BindingResponse> = withContext(Dispatchers.IO) {
        try {
            val request = BindingRequest(smiles, targetName)
            val body = gson.toJson(request)
                .toRequestBody("application/json".toMediaType())
            
            val httpRequest = okhttp3.Request.Builder()
                .url("$apiUrl/predictions/binding-affinity/")
                .post(body)
                .addHeader("Authorization", "Bearer $authToken")
                .addHeader("Content-Type", "application/json")
                .build()
            
            val response = client.newCall(httpRequest).execute()
            
            if (response.isSuccessful) {
                val data = gson.fromJson(
                    response.body?.string(),
                    BindingResponse::class.java
                )
                Result.success(data)
            } else {
                Result.failure(
                    Exception("API Error: ${response.code} ${response.message}")
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Usage in Activity
class DrugPredictionActivity : AppCompatActivity() {
    private val client = NeuroAIClient(authToken = "your-jwt-token")
    
    fun predictDrug(smiles: String, target: String) {
        lifecycleScope.launch {
            val result = client.predictBindingAffinity(smiles, target)
            result.onSuccess { response ->
                val score = response.binding_affinity.binding_score
                val confidence = response.binding_affinity.confidence
                updateUI(score, confidence)
            }.onFailure { error ->
                showError(error.message)
            }
        }
    }
    
    private fun updateUI(score: Double, confidence: String) {
        binding.predictionScore.text = "Binding: $score"
        binding.confidenceLevel.text = "Confidence: $confidence"
    }
}
```

### Java Implementation

```java
// NeuroAIAPI.java
import okhttp3.*;
import com.google.gson.*;
import java.io.IOException;
import java.util.concurrent.*;

public class NeuroAIAPI {
    private final String baseUrl = "https://api.neuroxai.com/v1";
    private final String authToken;
    private final OkHttpClient client = new OkHttpClient();
    private final Gson gson = new Gson();
    
    public NeuroAIAPI(String token) {
        this.authToken = token;
    }
    
    public void predictBinding(
        String smiles,
        String target,
        BindingCallback callback
    ) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.execute(() -> {
            try {
                // Build request
                JsonObject body = new JsonObject();
                body.addProperty("molecule_smiles", smiles);
                body.addProperty("target_name", target);
                
                RequestBody requestBody = RequestBody.create(
                    body.toString(),
                    MediaType.parse("application/json")
                );
                
                Request request = new Request.Builder()
                    .url(baseUrl + "/predictions/binding-affinity/")
                    .post(requestBody)
                    .addHeader("Authorization", "Bearer " + authToken)
                    .build();
                
                // Make request
                Response response = client.newCall(request).execute();
                
                if (response.isSuccessful()) {
                    String json = response.body().string();
                    JsonObject result = JsonParser.parseString(json)
                        .getAsJsonObject();
                    
                    double score = result.getAsJsonObject("binding_affinity")
                        .get("binding_score").getAsDouble();
                    String confidence = result.getAsJsonObject("binding_affinity")
                        .get("confidence").getAsString();
                    
                    callback.onSuccess(score, confidence);
                } else {
                    callback.onError("HTTP " + response.code());
                }
                
            } catch (IOException e) {
                callback.onError(e.getMessage());
            }
        });
    }
    
    public interface BindingCallback {
        void onSuccess(double score, String confidence);
        void onError(String error);
    }
}

// Usage
NeuroAIAPI api = new NeuroAIAPI("your-jwt-token");
api.predictBinding("CCO", "TNF-alpha", new NeuroAIAPI.BindingCallback() {
    @Override
    public void onSuccess(double score, String confidence) {
        Log.d("NeuroAI", "Binding score: " + score);
    }
    
    @Override
    public void onError(String error) {
        Log.e("NeuroAI", "Error: " + error);
    }
});
```

---

## Data Models for Android

### SMILES Input Validation

```java
public class SMILESValidator {
    // Valid examples
    private static final String[] VALID_SMILES = {
        "CCO",                                          // Ethanol
        "CC(C)Cc1ccc(cc1)C(C)C(O)=O",                  // Ibuprofen
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",                // Caffeine
        "CC(=O)Oc1ccccc1C(=O)O",                        // Aspirin
    };
    
    public static boolean isValidSMILES(String smiles) {
        // Check if SMILES contains valid chemistry notation
        if (smiles == null || smiles.isEmpty()) return false;
        
        String validChars = "CNOPSFClBrI()[]\\=/#@+-";
        for (char c : smiles.toCharArray()) {
            if (!Character.isLetterOrDigit(c) && validChars.indexOf(c) < 0) {
                return false;
            }
        }
        return true;
    }
}
```

### Score Display

```java
public class ScoreFormatter {
    public static String formatBindingScore(double score) {
        // Binding score 0-10 scale
        if (score >= 8) return "Excellent ⭐⭐⭐";
        if (score >= 6) return "Good ⭐⭐";
        if (score >= 4) return "Fair ⭐";
        return "Poor";
    }
    
    public static int getColorForConfidence(String confidence) {
        switch (confidence) {
            case "high": return Color.GREEN;
            case "medium": return Color.YELLOW;
            case "low": return Color.RED;
            default: return Color.GRAY;
        }
    }
    
    public static String formatToxicityRisk(String risk) {
        // low, medium, high
        switch (risk) {
            case "low": return "✅ Low Risk";
            case "medium": return "⚠️ Moderate Risk";
            case "high": return "❌ High Risk";
            default: return "Unknown";
        }
    }
}
```

---

## UI Patterns

### Prediction Results Display

```xml
<!-- activity_prediction_results.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <!-- Molecule Summary -->
    <CardView android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_margin="8dp">
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">
            
            <TextView
                android:text="Molecule Analysis"
                android:textSize="18sp"
                android:textStyle="bold" />
            
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp">
                <TextView
                    android:text="MW: "
                    android:layout_weight="1" />
                <TextView
                    android:id="@+id/molecularWeight"
                    android:layout_weight="1"
                    android:text="0.00" />
            </LinearLayout>
            
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content">
                <TextView
                    android:text="LogP: "
                    android:layout_weight="1" />
                <TextView
                    android:id="@+id/logp"
                    android:layout_weight="1"
                    android:text="0.00" />
            </LinearLayout>
        </LinearLayout>
    </CardView>
    
    <!-- Binding Affinity -->
    <CardView android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_margin="8dp">
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">
            
            <TextView
                android:text="Binding Affinity"
                android:textSize="18sp"
                android:textStyle="bold" />
            
            <ProgressBar
                android:id="@+id/bindingProgress"
                android:layout_width="match_parent"
                android:layout_height="12dp"
                android:layout_marginTop="8dp"
                android:progress="50"
                style="@android:style/Widget.ProgressBar.Horizontal" />
            
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="8dp">
                <TextView
                    android:text="Score: "
                    android:layout_weight="1" />
                <TextView
                    android:id="@+id/bindingScore"
                    android:layout_weight="1"
                    android:text="0.0"
                    android:textStyle="bold" />
            </LinearLayout>
            
            <TextView
                android:id="@+id/bindingConfidence"
                android:layout_marginTop="4dp"
                android:text="Confidence: high" />
        </LinearLayout>
    </CardView>
    
    <!-- Action Buttons -->
    <Button
        android:id="@+id/shareButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Share Results" />
    
    <Button
        android:id="@+id/saveDraftButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Save to Draft" />
</LinearLayout>
```

---

## Error Handling

### Common Errors

| Status | Code | Meaning | Solution |
|--------|------|---------|----------|
| 400 | BadRequest | Invalid SMILES | Validate SMILES format |
| 401 | Unauthorized | Missing/expired token | Refresh JWT token |
| 429 | TooManyRequests | Rate limited | Implement exponential backoff |
| 500 | ServerError | Model error | Retry with backoff |
| 504 | GatewayTimeout | Slow prediction | Implement timeout handling |

### Error Handling Example

```kotlin
suspend fun predictWithRetry(
    smiles: String,
    targetName: String,
    maxRetries: Int = 3
): Result<BindingResponse> {
    var lastError: Exception? = null
    
    repeat(maxRetries) { attempt ->
        try {
            val result = client.predictBindingAffinity(smiles, targetName)
            if (result.isSuccess) return result
            
            lastError = result.exceptionOrNull()
            
            // Wait before retry (exponential backoff)
            val delay = 1000L * (2 pow attempt)
            delay(delay)
            
        } catch (e: Exception) {
            lastError = e
        }
    }
    
    return Result.failure(lastError ?: Exception("Unknown error"))
}
```

---

## Performance Tips

### Caching Predictions

```kotlin
// Local cache for frequent molecules
val predictionCache = mutableMapOf<String, BindingResponse>()

suspend fun predictWithCache(smiles: String, target: String): Result<BindingResponse> {
    val cacheKey = "$smiles:$target"
    
    predictionCache[cacheKey]?.let {
        return Result.success(it)
    }
    
    val result = client.predictBindingAffinity(smiles, target)
    result.onSuccess {
        predictionCache[cacheKey] = it
    }
    return result
}
```

### Batch Requests

```kotlin
// Process multiple molecules efficiently
suspend fun batchPredict(
    molecules: List<Pair<String, String>>,  // (smiles, target)
    parallelism: Int = 3
): List<Result<BindingResponse>> {
    return molecules
        .chunked(parallelism)
        .flatMap { chunk ->
            chunk.map { (smiles, target) ->
                async { client.predictBindingAffinity(smiles, target) }
            }
            .awaitAll()
        }
}
```

---

## Summary

| Component | Details |
|-----------|---------|
| **API Base URL** | `https://api.neuroxai.com/v1` |
| **Authentication** | JWT Bearer token |
| **Response Format** | JSON |
| **Typical Response Time** | 2-4 seconds |
| **Available Endpoints** | 4 (binding, toxicity, drug-response, molecule-analysis) |
| **Mobile Ready** | ✅ Yes |
| **HTTPS Required** | ✅ Yes |

---

**For More Information**: See [PRETRAINED_MODELS_GUIDE.md](PRETRAINED_MODELS_GUIDE.md)

**Last Updated**: February 24, 2026

