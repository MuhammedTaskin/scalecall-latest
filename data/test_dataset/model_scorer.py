#!/usr/bin/env python3
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
