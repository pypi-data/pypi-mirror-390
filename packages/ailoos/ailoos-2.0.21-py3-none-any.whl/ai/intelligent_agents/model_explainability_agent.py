import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelExplainabilityAgent:
    """
    Agente inteligente que genera explicaciones sobre las decisiones o predicciones
    de los modelos de IA, mejorando la transparencia y la confianza.
    """
    def __init__(self):
        logger.info("ModelExplainabilityAgent inicializado. Listo para generar explicaciones de modelos.")

    def explain_prediction(self, 
                           model_id: str, 
                           input_data: Any, 
                           prediction: Any, 
                           explanation_type: str = "feature_importance") -> Dict[str, Any]:
        """
        Simula la generación de una explicación para una predicción de modelo.
        """
        explanation = {
            "model_id": model_id,
            "input_data": str(input_data), # Convertir a string para logging
            "prediction": str(prediction), # Convertir a string para logging
            "explanation_type": explanation_type,
            "explanation": "",
            "confidence": 0.0
        }

        if explanation_type == "feature_importance":
            # Simular importancia de características
            if isinstance(input_data, dict):
                important_features = random.sample(list(input_data.keys()), min(2, len(input_data)))
                explanation["explanation"] = f"Las características clave que influyeron en la predicción son: {', '.join(important_features)}."
            elif isinstance(input_data, str):
                words = input_data.split()
                if words:
                    explanation["explanation"] = f"Palabras clave que influyeron: '{random.choice(words)}' y '{random.choice(words)}'."
                else:
                    explanation["explanation"] = "No se encontraron características clave en la entrada."
            else:
                explanation["explanation"] = "Explicación de importancia de características no disponible para este tipo de entrada."
            explanation["confidence"] = random.uniform(0.7, 0.95)

        elif explanation_type == "simplified_rule":
            # Simular una regla simplificada
            if prediction == "positive":
                explanation["explanation"] = "El modelo predijo positivo porque la entrada contenía elementos X e Y."
            elif prediction == "negative":
                explanation["explanation"] = "El modelo predijo negativo porque la entrada carecía de Z."
            else:
                explanation["explanation"] = "Regla simplificada no disponible para esta predicción."
            explanation["confidence"] = random.uniform(0.6, 0.85)

        else:
            explanation["explanation"] = "Tipo de explicación no soportado."
            explanation["confidence"] = 0.0

        logger.info(f"Explicación generada para el modelo {model_id}: {explanation['explanation'][:70]}...")
        return explanation

if __name__ == "__main__":
    explainer = ModelExplainabilityAgent()

    # Ejemplo 1: Explicación de importancia de características para datos de texto
    logger.info("\n--- Explicación de importancia de características (texto) ---")
    text_input = "El cliente mostró un alto nivel de satisfacción con el servicio y el soporte técnico fue excelente."
    prediction_text = "Positive Sentiment"
    explanation_1 = explainer.explain_prediction("SentimentModel", text_input, prediction_text, "feature_importance")
    logger.info(f"Explicación: {explanation_1}")

    # Ejemplo 2: Explicación de importancia de características para datos estructurados
    logger.info("\n--- Explicación de importancia de características (estructurado) ---")
    structured_input = {"age": 30, "income": 50000, "credit_score": 750, "loan_amount": 10000}
    prediction_structured = "Low Risk"
    explanation_2 = explainer.explain_prediction("CreditRiskModel", structured_input, prediction_structured, "feature_importance")
    logger.info(f"Explicación: {explanation_2}")

    # Ejemplo 3: Explicación de regla simplificada
    logger.info("\n--- Explicación de regla simplificada ---")
    input_rule = "Datos de entrada para la regla"
    prediction_rule = "positive"
    explanation_3 = explainer.explain_prediction("FraudDetectionModel", input_rule, prediction_rule, "simplified_rule")
    logger.info(f"Explicación: {explanation_3}")

    logger.info("model_explainability_agent.py implementado y listo para generar explicaciones de modelos.")
