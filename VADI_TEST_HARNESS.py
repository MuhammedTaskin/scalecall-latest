#!/usr/bin/env python3
"""
VADI TEST HARNESS
Simulates TEKNOFEST scoring system for model evaluation
"""

import json
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class TestCategory(Enum):
    TOOL_ACCURACY = "tool_accuracy"
    HANDOFF_PRECISION = "handoff_precision"
    RESPONSE_QUALITY = "response_quality"
    EDGE_CASES = "edge_cases"
    LATENCY = "latency"

@dataclass
class TestResult:
    category: TestCategory
    score: float
    max_score: float
    details: Dict[str, Any]
    passed: bool

class VadiTestHarness:
    """Simulates Vadi testing environment"""
    
    def __init__(self):
        # Test weights (based on competition insight)
        self.weights = {
            TestCategory.TOOL_ACCURACY: 0.40,      # 40% - Most important
            TestCategory.RESPONSE_QUALITY: 0.30,   # 30% - Natural language
            TestCategory.HANDOFF_PRECISION: 0.20,  # 20% - Multi-agent
            TestCategory.EDGE_CASES: 0.10,         # 10% - Robustness
            TestCategory.LATENCY: 0.00             # Bonus points
        }
        
        # Valid tools for validation
        self.valid_tools = {
            "verify_user", "get_customer_status", "route_to_agent",
            "check_esim_status", "check_device_imei", "reissue_activation_code", 
            "create_tech_ticket", "get_customer_plan", "list_all_plans", 
            "change_customer_plan", "check_plan_compatibility",
            "get_last_bill", "get_unpaid_amount", "apply_campaign_discount", 
            "create_payment_note", "search_faq", "get_common_solutions", 
            "send_help_sms", "create_info_ticket", "escalate_to_human", 
            "end_conversation"
        }
        
        # Test scenarios
        self.test_scenarios = self.load_test_scenarios()
    
    def load_test_scenarios(self) -> List[Dict]:
        """Load test scenarios that Vadi might use"""
        
        return [
            # Scenario 1: Simple eSIM activation
            {
                "id": "test_001",
                "input": "eSIM'imi aktifleştiremedim, yardım eder misiniz?",
                "emotion": "confused",
                "expected_tools": ["verify_user", "check_esim_status", "reissue_activation_code"],
                "expected_agent": "TechAgent",
                "category": TestCategory.TOOL_ACCURACY
            },
            
            # Scenario 2: Angry billing complaint
            {
                "id": "test_002",
                "input": "Faturamda haksız ücret var! 500 TL ne demek ya!",
                "emotion": "angry",
                "expected_tools": ["verify_user", "get_last_bill", "get_customer_status"],
                "expected_agent": "BillingAgent",
                "requires_handoff": True,
                "category": TestCategory.HANDOFF_PRECISION
            },
            
            # Scenario 3: Plan upgrade
            {
                "id": "test_003",
                "input": "Daha fazla internet paketi istiyorum, ne önerirsiniz?",
                "emotion": "normal",
                "expected_tools": ["get_customer_plan", "list_all_plans", "check_plan_compatibility"],
                "expected_agent": "PlanAgent",
                "category": TestCategory.TOOL_ACCURACY
            },
            
            # Scenario 4: Complex multi-issue
            {
                "id": "test_004",
                "input": "Hem eSIM çalışmıyor hem de faturamda sorun var!",
                "emotion": "frustrated",
                "expected_tools": ["verify_user", "check_esim_status", "get_last_bill"],
                "expected_agents": ["RouterAgent", "TechAgent", "BillingAgent"],
                "requires_multiple_handoffs": True,
                "category": TestCategory.EDGE_CASES
            },
            
            # Scenario 5: FAQ query
            {
                "id": "test_005",
                "input": "5G hizmeti hangi şehirlerde var?",
                "emotion": "curious",
                "expected_tools": ["search_faq", "get_common_solutions"],
                "expected_agent": "FAQAgent",
                "category": TestCategory.RESPONSE_QUALITY
            }
        ]
    
    def test_tool_accuracy(self, model_output: Dict, expected_tools: List[str]) -> TestResult:
        """Test if model calls correct tools"""
        
        model_tools = set(model_output.get("tools", []))
        expected_set = set(expected_tools)
        
        # Calculate precision and recall
        if len(model_tools) == 0:
            score = 0
        else:
            correct = model_tools & expected_set
            precision = len(correct) / len(model_tools) if model_tools else 0
            recall = len(correct) / len(expected_set) if expected_set else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            score = f1 * 100
        
        # Check for invalid tools
        invalid_tools = model_tools - self.valid_tools
        if invalid_tools:
            score *= 0.5  # Heavy penalty for invalid tools
        
        return TestResult(
            category=TestCategory.TOOL_ACCURACY,
            score=score,
            max_score=100,
            details={
                "expected": list(expected_set),
                "predicted": list(model_tools),
                "invalid": list(invalid_tools)
            },
            passed=score >= 80
        )
    
    def test_handoff_precision(self, model_output: Dict, scenario: Dict) -> TestResult:
        """Test handoff accuracy"""
        
        next_agent = model_output.get("next_agent")
        expected_agent = scenario.get("expected_agent")
        
        score = 0
        details = {}
        
        if scenario.get("requires_handoff"):
            if next_agent == expected_agent:
                score = 100
                details["status"] = "Correct handoff"
            elif next_agent:
                score = 50  # Partial credit for attempting handoff
                details["status"] = "Wrong agent"
            else:
                score = 0
                details["status"] = "Missing handoff"
        else:
            # Should not handoff
            if not next_agent:
                score = 100
                details["status"] = "Correctly no handoff"
            else:
                score = 0
                details["status"] = "Unnecessary handoff"
        
        details["expected"] = expected_agent
        details["predicted"] = next_agent
        
        return TestResult(
            category=TestCategory.HANDOFF_PRECISION,
            score=score,
            max_score=100,
            details=details,
            passed=score >= 70
        )
    
    def test_response_quality(self, model_output: Dict, scenario: Dict) -> TestResult:
        """Test Turkish language quality and professionalism"""
        
        response = model_output.get("response", "")
        score = 100
        details = []
        
        # Check response exists
        if not response:
            return TestResult(
                category=TestCategory.RESPONSE_QUALITY,
                score=0,
                max_score=100,
                details={"error": "No response"},
                passed=False
            )
        
        # Length check
        if len(response) < 20:
            score -= 20
            details.append("Too short")
        elif len(response) > 500:
            score -= 10
            details.append("Too long")
        
        # Professional tone markers
        professional_markers = ["Sayın", "Rica ederim", "Yardımcı", "İyi günler"]
        if not any(marker in response for marker in professional_markers):
            score -= 15
            details.append("Lacks professional tone")
        
        # Emotion handling
        if scenario.get("emotion") == "angry":
            calming_phrases = ["Anlıyorum", "Özür", "Hemen", "Çözüm"]
            if not any(phrase in response for phrase in calming_phrases):
                score -= 20
                details.append("Poor anger handling")
        
        # Turkish character check
        turkish_chars = "çğıöşüÇĞİÖŞÜ"
        if not any(char in response for char in turkish_chars):
            score -= 30
            details.append("Missing Turkish characters")
        
        return TestResult(
            category=TestCategory.RESPONSE_QUALITY,
            score=max(0, score),
            max_score=100,
            details={"issues": details, "response_length": len(response)},
            passed=score >= 70
        )
    
    def test_latency(self, response_time_ms: float) -> TestResult:
        """Test response latency"""
        
        if response_time_ms < 100:
            score = 100
        elif response_time_ms < 300:
            score = 90
        elif response_time_ms < 500:
            score = 80
        elif response_time_ms < 1000:
            score = 60
        else:
            score = 0
        
        return TestResult(
            category=TestCategory.LATENCY,
            score=score,
            max_score=100,
            details={"response_time_ms": response_time_ms},
            passed=response_time_ms < 500
        )
    
    def run_full_test(self, model_inference_fn) -> Dict:
        """Run complete Vadi test suite"""
        
        print("🎯 VADI TEST HARNESS")
        print("="*60)
        
        all_results = []
        category_scores = {cat: [] for cat in TestCategory}
        
        for scenario in self.test_scenarios:
            print(f"\n📝 Testing: {scenario['id']}")
            print(f"   Input: {scenario['input'][:50]}...")
            
            # Run inference
            start_time = time.time()
            model_output = model_inference_fn(
                transcript=scenario["input"],
                emotion=scenario.get("emotion", "normal")
            )
            latency = (time.time() - start_time) * 1000
            
            # Run tests based on scenario category
            if scenario["category"] == TestCategory.TOOL_ACCURACY:
                result = self.test_tool_accuracy(
                    model_output, 
                    scenario["expected_tools"]
                )
            elif scenario["category"] == TestCategory.HANDOFF_PRECISION:
                result = self.test_handoff_precision(model_output, scenario)
            elif scenario["category"] == TestCategory.RESPONSE_QUALITY:
                result = self.test_response_quality(model_output, scenario)
            elif scenario["category"] == TestCategory.EDGE_CASES:
                # Complex test combining multiple aspects
                tool_result = self.test_tool_accuracy(
                    model_output,
                    scenario["expected_tools"]
                )
                result = TestResult(
                    category=TestCategory.EDGE_CASES,
                    score=(tool_result.score * 0.7 + 30),  # Partial credit for attempt
                    max_score=100,
                    details={"tool_score": tool_result.score},
                    passed=tool_result.score >= 60
                )
            
            # Add latency test
            latency_result = self.test_latency(latency)
            
            # Store results
            all_results.append(result)
            category_scores[result.category].append(result.score)
            
            # Print result
            status = "✅" if result.passed else "❌"
            print(f"   {status} {result.category.value}: {result.score:.1f}/100")
            if latency_result.score >= 80:
                print(f"   ⚡ Latency: {latency:.0f}ms")
        
        # Calculate final score
        final_score = 0
        for category, weight in self.weights.items():
            if category in category_scores and category_scores[category]:
                avg_score = sum(category_scores[category]) / len(category_scores[category])
                final_score += avg_score * weight
        
        # Generate report
        report = {
            "final_score": final_score,
            "pass": final_score >= 75,
            "category_breakdown": {},
            "recommendations": []
        }
        
        for category in TestCategory:
            if category in category_scores and category_scores[category]:
                avg = sum(category_scores[category]) / len(category_scores[category])
                report["category_breakdown"][category.value] = {
                    "average_score": avg,
                    "weight": self.weights[category],
                    "contribution": avg * self.weights[category]
                }
                
                if avg < 70:
                    report["recommendations"].append(
                        f"Improve {category.value}: Currently at {avg:.1f}%"
                    )
        
        # Print summary
        print("\n" + "="*60)
        print("📊 VADI TEST RESULTS")
        print(f"   Final Score: {final_score:.1f}/100")
        print(f"   Status: {'✅ PASS' if report['pass'] else '❌ FAIL'}")
        
        print("\n📈 Category Breakdown:")
        for cat, data in report["category_breakdown"].items():
            print(f"   {cat}: {data['average_score']:.1f}% (weight: {data['weight']*100:.0f}%)")
        
        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   - {rec}")
        
        return report

def mock_model_inference(transcript: str, emotion: str) -> Dict:
    """Mock model for testing the harness"""
    
    # Simple rule-based responses for testing
    response = "Merhaba, size nasıl yardımcı olabilirim?"
    tools = []
    next_agent = None
    
    if "eSIM" in transcript:
        tools = ["verify_user", "check_esim_status"]
        next_agent = "TechAgent"
        response = "eSIM sorununuzu hemen kontrol ediyorum."
    elif "fatura" in transcript.lower():
        tools = ["verify_user", "get_last_bill"]
        next_agent = "BillingAgent"
        response = "Faturanızı inceliyorum, lütfen bekleyin."
    elif "paket" in transcript or "internet" in transcript:
        tools = ["get_customer_plan", "list_all_plans"]
        next_agent = "PlanAgent"
        response = "Size uygun paketleri listeliyorum."
    elif "5G" in transcript:
        tools = ["search_faq"]
        next_agent = "FAQAgent"
        response = "5G hizmetimiz hakkında bilgi veriyorum."
    
    return {
        "response": response,
        "tools": tools,
        "next_agent": next_agent
    }

def main():
    print("🚀 VADI TEST HARNESS READY")
    print("="*60)
    
    # Initialize harness
    harness = VadiTestHarness()
    
    # Run tests with mock model
    print("\n🧪 Running with mock model...")
    report = harness.run_full_test(mock_model_inference)
    
    # Save report
    with open("vadi_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to vadi_test_report.json")
    
    # Competition readiness
    if report["final_score"] >= 90:
        print("\n🏆 MODEL IS COMPETITION READY!")
    elif report["final_score"] >= 75:
        print("\n⚡ Model passes but needs optimization")
    else:
        print("\n⚠️ Model needs more training")

if __name__ == "__main__":
    main()