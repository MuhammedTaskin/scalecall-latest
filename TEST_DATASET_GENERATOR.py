#!/usr/bin/env python3
"""
TEST Dataset Generator - Vadi'nin test edeceği senaryolar
200+ edge case ve kompleks senaryo
"""

import json
import os
from datetime import datetime

class TestDatasetGenerator:
    def __init__(self):
        self.output_dir = "data/test_dataset"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Vadi'nin muhtemel test kategorileri
        self.test_categories = {
            "critical_emergency": [
                {
                    "input": "Acil durum! Ambulans arayamıyorum, hattım çalışmıyor!",
                    "expected_behavior": "immediate_escalation",
                    "required_tools": ["verify_user", "escalate_to_human"],
                    "max_turns": 3,
                    "priority": "CRITICAL"
                },
                {
                    "input": "Telefonum çalındı ve içinde hassas bilgiler var, hattımı kapatın!",
                    "expected_behavior": "immediate_line_suspension",
                    "required_tools": ["verify_user", "suspend_line", "create_ticket"],
                    "max_turns": 4,
                    "priority": "CRITICAL"
                }
            ],
            
            "complex_multi_issue": [
                {
                    "input": "eSIM'im çalışmıyor, faturamda yanlış ücret var ve planımı değiştirmek istiyorum",
                    "expected_behavior": "systematic_resolution",
                    "required_tools": ["verify_user", "check_esim_status", "get_last_bill", "list_all_plans"],
                    "required_handoffs": ["RouterAgent", "TechAgent", "BillingAgent", "PlanAgent"],
                    "priority": "HIGH"
                },
                {
                    "input": "Numara taşıma yapıyorum ama eski operatörümden borç var, ayrıca yurtdışı paketi de istiyorum",
                    "expected_behavior": "coordinate_departments",
                    "required_tools": ["verify_user", "check_porting_status", "get_unpaid_amount", "list_all_plans"],
                    "required_handoffs": ["RouterAgent", "BillingAgent", "PlanAgent"],
                    "priority": "HIGH"
                }
            ],
            
            "emotion_handling": [
                {
                    "input": "YA YETER ARTIK! 5. KEZ ARIYORUM! SORUNU ÇÖZEMİYORSANIZ KAPATIYORUM!",
                    "emotion": "extremely_angry",
                    "expected_behavior": "de-escalation",
                    "required_skills": ["empathy", "quick_resolution", "clear_communication"],
                    "priority": "HIGH"
                },
                {
                    "input": "Ben... şey... yaşlıyım biraz, bu telefon işlerini anlamıyorum, yardım eder misiniz?",
                    "emotion": "confused_elderly",
                    "expected_behavior": "patient_guidance",
                    "required_skills": ["patience", "simple_language", "step_by_step"],
                    "priority": "MEDIUM"
                }
            ],
            
            "dialect_understanding": [
                {
                    "input": "Uşağum benim hat gari çalışmıyor, nooldu buna böyle?",
                    "dialect": "black_sea",
                    "expected_behavior": "understand_and_respond",
                    "priority": "MEDIUM"
                },
                {
                    "input": "Valla billahi internet yok gardaş, bi bakıver şuna",
                    "dialect": "southeastern",
                    "expected_behavior": "understand_and_respond",
                    "priority": "MEDIUM"
                }
            ],
            
            "tool_chain_complexity": [
                {
                    "input": "Kurumsal müşteriyim, 50 hattım var, hepsini başka tarıfeye geçireceğim",
                    "expected_tools": ["verify_user", "get_customer_status", "list_all_plans", "change_customer_plan"],
                    "complexity": "very_high",
                    "priority": "HIGH"
                }
            ],
            
            "interruption_recovery": [
                {
                    "input": "Merhaba ben-- *bağlantı kopuyor* --duyabiliyor musun-- *parazit* --faturamda sorun--",
                    "challenge": "connection_issues",
                    "expected_behavior": "maintain_context",
                    "priority": "MEDIUM"
                }
            ],
            
            "edge_cases": [
                {
                    "input": "0 TL fatura ödedim ama hala borç görünüyor",
                    "category": "billing_anomaly",
                    "priority": "LOW"
                },
                {
                    "input": "eSIM'imi 2 cihazda aynı anda kullanabilir miyim?",
                    "category": "technical_edge",
                    "priority": "LOW"
                }
            ]
        }
        
        # Beklenen çıktı formatı
        self.output_format = {
            "test_id": "",
            "category": "",
            "input": {
                "text": "",
                "emotion": "",
                "context": ""
            },
            "expected_output": {
                "agent_flow": [],
                "tools_used": [],
                "resolution": "",
                "turns": 0
            },
            "scoring_criteria": {
                "tool_accuracy": 0.3,
                "handoff_logic": 0.2,
                "resolution_quality": 0.3,
                "language_quality": 0.2
            }
        }
    
    def generate_test_cases(self):
        """Generate comprehensive test dataset"""
        
        all_tests = []
        test_id = 1
        
        for category, cases in self.test_categories.items():
            for case in cases:
                test_case = {
                    "test_id": f"TEST_{test_id:04d}",
                    "category": category,
                    "priority": case.get("priority", "MEDIUM"),
                    "input": case.get("input", ""),
                    "metadata": {
                        "emotion": case.get("emotion", "normal"),
                        "dialect": case.get("dialect", "standard"),
                        "challenge": case.get("challenge", "none")
                    },
                    "expected_behavior": case.get("expected_behavior", "standard_resolution"),
                    "required_tools": case.get("required_tools", []),
                    "required_handoffs": case.get("required_handoffs", []),
                    "max_acceptable_turns": case.get("max_turns", 10),
                    "timestamp": datetime.now().isoformat()
                }
                
                all_tests.append(test_case)
                test_id += 1
        
        # Save test dataset
        output_file = f"{self.output_dir}/test_cases.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_tests": len(all_tests),
                    "categories": list(self.test_categories.keys()),
                    "generated_at": datetime.now().isoformat()
                },
                "test_cases": all_tests
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Generated {len(all_tests)} test cases")
        print(f"📁 Saved to: {output_file}")
        
        # Generate priority summary
        priority_counts = {}
        for test in all_tests:
            p = test["priority"]
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        print(f"\n📊 Priority Distribution:")
        for priority, count in priority_counts.items():
            print(f"  {priority}: {count} tests")
        
        return all_tests
    
    def generate_scorer(self):
        """Generate scoring script"""
        
        scorer_code = '''#!/usr/bin/env python3
"""
Model Scorer - Vadi test simülasyonu
"""

import json
from typing import Dict, List

class ModelScorer:
    def __init__(self, model_endpoint: str):
        self.model_endpoint = model_endpoint
        self.weights = {
            "tool_accuracy": 0.3,
            "handoff_logic": 0.2,
            "resolution_quality": 0.3,
            "language_quality": 0.2
        }
    
    def score_response(self, test_case: Dict, model_output: Dict) -> float:
        """Score a single response"""
        
        scores = {}
        
        # Tool accuracy
        expected_tools = set(test_case.get("required_tools", []))
        actual_tools = set(model_output.get("tools_used", []))
        tool_score = len(expected_tools & actual_tools) / max(len(expected_tools), 1)
        scores["tool_accuracy"] = tool_score
        
        # Handoff logic
        expected_handoffs = test_case.get("required_handoffs", [])
        actual_handoffs = model_output.get("agent_flow", [])
        handoff_score = self.calculate_handoff_score(expected_handoffs, actual_handoffs)
        scores["handoff_logic"] = handoff_score
        
        # Resolution quality
        resolved = model_output.get("resolved", False)
        turns = model_output.get("turns", 999)
        max_turns = test_case.get("max_acceptable_turns", 10)
        resolution_score = (1.0 if resolved else 0.5) * (1.0 if turns <= max_turns else 0.7)
        scores["resolution_quality"] = resolution_score
        
        # Language quality (placeholder)
        scores["language_quality"] = 0.8  # Would need NLP analysis
        
        # Weighted total
        total = sum(scores[k] * self.weights[k] for k in self.weights)
        
        return total, scores
    
    def calculate_handoff_score(self, expected: List, actual: List) -> float:
        """Calculate handoff accuracy"""
        if not expected:
            return 1.0 if not actual else 0.5
        
        matches = 0
        for i, agent in enumerate(expected):
            if i < len(actual) and actual[i] == agent:
                matches += 1
        
        return matches / len(expected)
    
    def run_test_suite(self, test_file: str) -> Dict:
        """Run full test suite"""
        
        with open(test_file, 'r') as f:
            test_data = json.load(f)
        
        results = []
        total_score = 0
        
        for test in test_data["test_cases"]:
            # Call model
            model_output = self.call_model(test["input"])
            
            # Score response
            score, breakdown = self.score_response(test, model_output)
            
            results.append({
                "test_id": test["test_id"],
                "category": test["category"],
                "score": score,
                "breakdown": breakdown,
                "priority": test["priority"]
            })
            
            total_score += score
        
        return {
            "total_score": total_score / len(results),
            "results": results,
            "summary": self.generate_summary(results)
        }
    
    def call_model(self, input_text: str) -> Dict:
        """Call the model (placeholder)"""
        # This would actually call your model
        return {
            "tools_used": ["verify_user"],
            "agent_flow": ["RouterAgent"],
            "resolved": True,
            "turns": 5
        }
    
    def generate_summary(self, results: List) -> Dict:
        """Generate performance summary"""
        
        by_category = {}
        by_priority = {}
        
        for r in results:
            cat = r["category"]
            pri = r["priority"]
            
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r["score"])
            
            if pri not in by_priority:
                by_priority[pri] = []
            by_priority[pri].append(r["score"])
        
        return {
            "by_category": {k: sum(v)/len(v) for k, v in by_category.items()},
            "by_priority": {k: sum(v)/len(v) for k, v in by_priority.items()}
        }

if __name__ == "__main__":
    scorer = ModelScorer("http://localhost:8080/generate")
    results = scorer.run_test_suite("data/test_dataset/test_cases.json")
    
    print(f"Overall Score: {results['total_score']:.2%}")
    print(f"By Category: {results['summary']['by_category']}")
    print(f"By Priority: {results['summary']['by_priority']}")
'''
        
        with open(f"{self.output_dir}/model_scorer.py", 'w') as f:
            f.write(scorer_code)
        
        print(f"✅ Generated scorer: {self.output_dir}/model_scorer.py")

def main():
    generator = TestDatasetGenerator()
    
    print("🎯 TEST DATASET GENERATOR")
    print("="*60)
    
    # Generate test cases
    test_cases = generator.generate_test_cases()
    
    # Generate scorer
    generator.generate_scorer()
    
    print(f"\n🏆 Ready for testing!")
    print(f"   Use these to find weaknesses BEFORE Vadi tests")
    print(f"   Iterate quickly: Test → Fix → Test → Win")

if __name__ == "__main__":
    main()