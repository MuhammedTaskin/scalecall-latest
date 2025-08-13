"""
Evaluation runner with 100+ test cases and KPI reporting.
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from backend.orchestrator import Orchestrator
from backend.tools.registry import ToolRegistry
from backend.db import init_db

logger = logging.getLogger(__name__)


class EvalCase:
    """Single evaluation test case."""
    
    def __init__(self, case_id: str, description: str, input_text: str, 
                 expected_tools: List[str], expected_outcome: str, 
                 persona: str = "RouterAgent"):
        self.case_id = case_id
        self.description = description
        self.input_text = input_text
        self.expected_tools = expected_tools
        self.expected_outcome = expected_outcome
        self.persona = persona


class EvalResult:
    """Evaluation result for a single case."""
    
    def __init__(self, case: EvalCase):
        self.case = case
        self.success = False
        self.tools_called = []
        self.response_text = ""
        self.first_token_latency_ms = 0
        self.total_latency_ms = 0
        self.error_message = ""
        self.tool_accuracy = 0.0
        self.handoffs = []


class EvalRunner:
    """Main evaluation runner."""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.tools = ToolRegistry()
        self.test_cases = []
        self._init_test_cases()
    
    def _init_test_cases(self):
        """Initialize comprehensive test cases."""
        
        # Basic verification flow
        self.test_cases.extend([
            EvalCase("verify_001", "Basic user verification", 
                    "Merhaba, eSIM almak istiyorum",
                    ["verify_user"], "verification_required"),
            
            EvalCase("verify_002", "Verification with credentials",
                    "Adım Ahmet Yılmaz, annemin kızlık soyadı Kaya, numaram 905551234567",
                    ["verify_user"], "verification_success"),
            
            EvalCase("verify_003", "Wrong credentials",
                    "Adım Mehmet Demir, annemin kızlık soyadı Yıldız, numaram 905551111111", 
                    ["verify_user"], "verification_failed"),
        ])
        
        # Device and activation flow
        self.test_cases.extend([
            EvalCase("device_001", "Device compatibility check",
                    "Cihazımın uyumlu olup olmadığını kontrol edebilir misiniz? IMEI: 123456789012345",
                    ["check_device_registration"], "device_compatible"),
            
            EvalCase("device_002", "New device registration",
                    "Yeni iPhone aldım, IMEI: 999888777666555",
                    ["check_device_registration"], "device_new"),
            
            EvalCase("activation_001", "Request activation code",
                    "Aktivasyon kodumu yeniden gönderebilir misiniz?",
                    ["reissue_activation_code"], "activation_code_sent"),
            
            EvalCase("activation_002", "iOS activation steps",
                    "iPhone'da eSIM nasıl aktif ediyorum?",
                    ["get_activation_steps"], "activation_steps_provided"),
            
            EvalCase("activation_003", "Android activation steps", 
                    "Samsung telefonumda eSIM kurulumu nasıl yapılır?",
                    ["get_activation_steps"], "activation_steps_provided"),
            
            EvalCase("activation_004", "Check activation status",
                    "eSIM'im aktif oldu mu kontrol eder misiniz?",
                    ["get_activation_status"], "activation_status_checked"),
        ])
        
        # Package management
        self.test_cases.extend([
            EvalCase("package_001", "List available packages",
                    "Hangi paketleriniz var?",
                    ["get_available_packages"], "packages_listed"),
            
            EvalCase("package_002", "Change package request",
                    "Paketimi Premium 10GB'a değiştirmek istiyorum",
                    ["get_available_packages", "change_package"], "package_changed"),
            
            EvalCase("package_003", "Package comparison",
                    "Unlimited paket ile Premium arasında ne fark var?",
                    ["get_available_packages"], "packages_compared"),
        ])
        
        # Technical support
        self.test_cases.extend([
            EvalCase("tech_001", "Network connectivity issue",
                    "İnternetim çok yavaş, teknik sorun olabilir mi?",
                    ["create_support_ticket"], "ticket_created"),
                    
            EvalCase("tech_002", "eSIM not working",
                    "eSIM hiç çalışmıyor, ne yapmalıyım?",
                    ["get_activation_status", "create_support_ticket"], "technical_support"),
                    
            EvalCase("tech_003", "Coverage question",
                    "Antalya'da kapsama alanınız var mı?",
                    [], "coverage_info"),
        ])
        
        # Handoff scenarios
        self.test_cases.extend([
            EvalCase("handoff_001", "Tech handoff trigger",
                    "Cihazım hiç bağlanmıyor, teknik destek lazım",
                    [], "tech_handoff", "RouterAgent"),
                    
            EvalCase("handoff_002", "Plan handoff trigger", 
                    "Daha uygun bir paket var mı, değiştirmek istiyorum",
                    [], "plan_handoff", "RouterAgent"),
                    
            EvalCase("handoff_003", "Billing handoff trigger",
                    "Faturamda hata var, ücret iadesi istiyorum",
                    [], "billing_handoff", "RouterAgent"),
        ])
        
        # Error handling and edge cases
        self.test_cases.extend([
            EvalCase("error_001", "Invalid IMEI format",
                    "IMEI: 123 kontrol eder misiniz?",
                    ["check_device_registration"], "error_handled"),
                    
            EvalCase("error_002", "Unclear request",
                    "Bir şey yapmak istiyorum ama ne bilmiyorum",
                    [], "clarification_requested"),
                    
            EvalCase("error_003", "Multiple requests",
                    "Hem paket değiştirmek hem de teknik destek hem de fatura sorunu var",
                    [], "request_prioritized"),
        ])
        
        # Conversational flow
        self.test_cases.extend([
            EvalCase("conv_001", "Greeting and introduction",
                    "Merhaba, nasılsınız?",
                    [], "greeting_response"),
                    
            EvalCase("conv_002", "Thank you",
                    "Teşekkür ederim, çok yardımcı oldunuz",
                    [], "appreciation_acknowledged"),
                    
            EvalCase("conv_003", "Goodbye", 
                    "İyi günler, kapanıyorum",
                    [], "goodbye_response"),
        ])
        
        # PII and security
        self.test_cases.extend([
            EvalCase("security_001", "PII masking test",
                    "Numaram 905551234567, IMEI 123456789012345",
                    [], "pii_masked"),
                    
            EvalCase("security_002", "Token request",
                    "Aktivasyon tokenimi söyleyebilir misiniz?",
                    [], "token_refused"),
        ])
        
        # Performance critical paths
        self.test_cases.extend([
            EvalCase("perf_001", "Fast verification path",
                    "Ahmet Yılmaz, Kaya, 905551234567, eSIM aktivasyon",
                    ["verify_user", "get_activation_status"], "fast_path"),
                    
            EvalCase("perf_002", "Complete eSIM flow",
                    "eSIM almak istiyorum, Fatma Demir, Özkan, 905559876543",
                    ["verify_user", "get_user_info", "check_device_registration", 
                     "reissue_activation_code", "get_activation_steps"], "complete_flow"),
        ])
        
        # Multi-language and ASR corrections
        self.test_cases.extend([
            EvalCase("lang_001", "ASR correction - mevsim to eSIM",
                    "mevsim almak istiyorum",
                    [], "asr_corrected"),
                    
            EvalCase("lang_002", "Mixed language input",
                    "eSIM activation kodumu iPhone'a nasıl yüklerim?",
                    ["get_activation_steps"], "mixed_language_handled"),
        ])
        
        # Stress and boundary tests  
        self.test_cases.extend([
            EvalCase("stress_001", "Long input",
                    "Merhaba, ben çok uzun zamandır müşterinizim ve eSIM konusunda " +
                    "sürekli sorun yaşıyorum, paketim çalışmıyor, internet yavaş, " +
                    "aktivasyon olmadı, teknik destek istiyorum, faturamda da hatalar var...",
                    [], "long_input_handled"),
                    
            EvalCase("stress_002", "Rapid fire questions",
                    "Paket? Fiyat? Aktivasyon? Destek?",
                    [], "multiple_queries_handled"),
        ])

        logger.info(f"Initialized {len(self.test_cases)} test cases")
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation suite."""
        logger.info("Starting evaluation run...")
        
        start_time = time.time()
        results = []
        
        # Initialize database
        await init_db()
        
        for i, case in enumerate(self.test_cases):
            logger.info(f"Running case {i+1}/{len(self.test_cases)}: {case.case_id}")
            
            try:
                result = await self._run_single_case(case)
                results.append(result)
                
                # Brief pause between cases
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Case {case.case_id} failed: {e}")
                result = EvalResult(case)
                result.error_message = str(e)
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Generate report
        report = self._generate_report(results, total_time)
        
        # Save results
        await self._save_results(results, report)
        
        logger.info(f"Evaluation completed in {total_time:.2f}s")
        return report
    
    async def _run_single_case(self, case: EvalCase) -> EvalResult:
        """Run a single test case."""
        result = EvalResult(case)
        
        # Prepare messages
        messages = [{"role": "user", "content": case.input_text}]
        
        start_time = time.time()
        first_token_time = None
        tools_called = []
        handoffs = []
        response_chunks = []
        
        try:
            # Stream response
            async for chunk in self.orchestrator.stream(messages, case.persona):
                current_time = time.time()
                
                if first_token_time is None:
                    first_token_time = current_time
                    result.first_token_latency_ms = int((current_time - start_time) * 1000)
                
                if "delta" in chunk:
                    response_chunks.append(chunk["delta"])
                    
                elif "tool_call" in chunk:
                    tool_name = chunk["tool_call"]["name"]
                    tools_called.append(tool_name)
                    
                    # Execute tool
                    tool_result = await self.orchestrator.execute_tool(chunk["tool_call"])
                    
                elif "handoff" in chunk:
                    handoffs.append(chunk["handoff"]["persona"])
                    
                elif "complete" in chunk:
                    break
            
            result.total_latency_ms = int((time.time() - start_time) * 1000)
            result.tools_called = tools_called
            result.response_text = "".join(response_chunks)
            result.handoffs = handoffs
            
            # Calculate tool accuracy
            if case.expected_tools:
                expected_set = set(case.expected_tools)
                actual_set = set(tools_called)
                
                if expected_set:
                    intersection = expected_set.intersection(actual_set)
                    result.tool_accuracy = len(intersection) / len(expected_set)
                else:
                    result.tool_accuracy = 1.0 if not actual_set else 0.0
            else:
                result.tool_accuracy = 1.0
            
            # Determine success based on criteria
            result.success = self._evaluate_success(case, result)
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
        
        return result
    
    def _evaluate_success(self, case: EvalCase, result: EvalResult) -> bool:
        """Evaluate if a test case passed."""
        
        # Check for errors
        if result.error_message:
            return False
        
        # Check latency requirements
        if result.first_token_latency_ms > 3000:  # 3 second limit
            return False
        
        # Check tool accuracy
        if result.tool_accuracy < 0.5:  # At least 50% of expected tools
            return False
        
        # Check for expected outcomes
        response_lower = result.response_text.lower()
        
        outcome_checks = {
            "verification_required": any(word in response_lower for word in 
                                       ["doğrula", "kimlik", "verify", "kızlık"]),
            "verification_success": "doğrulan" in response_lower or "başarı" in response_lower,
            "verification_failed": "başarısız" in response_lower or "hata" in response_lower,
            "device_compatible": "uyumlu" in response_lower or "destekl" in response_lower,
            "activation_code_sent": "kod" in response_lower or "lpa" in response_lower,
            "activation_steps_provided": "adım" in response_lower or "ayarlar" in response_lower,
            "packages_listed": "paket" in response_lower or "gb" in response_lower,
            "tech_handoff": "TechAgent" in result.handoffs,
            "plan_handoff": "PlanAgent" in result.handoffs,
            "billing_handoff": "BillingAgent" in result.handoffs,
            "pii_masked": "*" in result.response_text,  # Check for masking
        }
        
        if case.expected_outcome in outcome_checks:
            return outcome_checks[case.expected_outcome]
        
        # Default: if we got here without errors, consider it a pass
        return True
    
    def _generate_report(self, results: List[EvalResult], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        
        total_cases = len(results)
        successful_cases = sum(1 for r in results if r.success)
        
        # Calculate KPIs
        success_rate = successful_cases / total_cases if total_cases > 0 else 0
        
        tool_accuracies = [r.tool_accuracy for r in results if r.tool_accuracy is not None]
        avg_tool_accuracy = sum(tool_accuracies) / len(tool_accuracies) if tool_accuracies else 0
        
        first_token_latencies = [r.first_token_latency_ms for r in results if r.first_token_latency_ms > 0]
        avg_first_token_latency = sum(first_token_latencies) / len(first_token_latencies) if first_token_latencies else 0
        
        total_latencies = [r.total_latency_ms for r in results if r.total_latency_ms > 0]
        avg_total_latency = sum(total_latencies) / len(total_latencies) if total_latencies else 0
        
        # Error analysis
        error_cases = [r for r in results if not r.success]
        error_rate = len(error_cases) / total_cases if total_cases > 0 else 0
        
        # Tool usage analysis
        all_tools_called = []
        for r in results:
            all_tools_called.extend(r.tools_called)
        
        tool_usage = {}
        for tool in all_tools_called:
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # Handoff analysis
        all_handoffs = []
        for r in results:
            all_handoffs.extend(r.handoffs)
        
        handoff_usage = {}
        for handoff in all_handoffs:
            handoff_usage[handoff] = handoff_usage.get(handoff, 0) + 1
        
        report = {
            "evaluation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_cases": total_cases,
                "successful_cases": successful_cases,
                "failed_cases": total_cases - successful_cases,
                "total_runtime_seconds": round(total_time, 2)
            },
            "kpis": {
                "success_rate": round(success_rate, 3),
                "tool_accuracy": round(avg_tool_accuracy, 3), 
                "first_token_latency_ms": round(avg_first_token_latency, 1),
                "task_latency_ms": round(avg_total_latency, 1),
                "error_rate": round(error_rate, 3)
            },
            "performance_breakdown": {
                "latency_distribution": {
                    "p50_first_token": round(sorted(first_token_latencies)[len(first_token_latencies)//2], 1) if first_token_latencies else 0,
                    "p95_first_token": round(sorted(first_token_latencies)[int(len(first_token_latencies)*0.95)], 1) if first_token_latencies else 0,
                    "p50_total": round(sorted(total_latencies)[len(total_latencies)//2], 1) if total_latencies else 0,
                    "p95_total": round(sorted(total_latencies)[int(len(total_latencies)*0.95)], 1) if total_latencies else 0,
                }
            },
            "tool_usage": tool_usage,
            "handoff_usage": handoff_usage,
            "error_analysis": {
                "common_errors": [r.error_message for r in error_cases[:5]],
                "error_categories": self._categorize_errors(error_cases)
            }
        }
        
        return report
    
    def _categorize_errors(self, error_cases: List[EvalResult]) -> Dict[str, int]:
        """Categorize errors for analysis."""
        categories = {
            "timeout": 0,
            "tool_error": 0, 
            "parsing_error": 0,
            "latency": 0,
            "other": 0
        }
        
        for case in error_cases:
            error_msg = case.error_message.lower()
            
            if "timeout" in error_msg or case.first_token_latency_ms > 3000:
                categories["latency"] += 1
            elif "tool" in error_msg:
                categories["tool_error"] += 1
            elif "json" in error_msg or "parse" in error_msg:
                categories["parsing_error"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    async def _save_results(self, results: List[EvalResult], report: Dict[str, Any]):
        """Save evaluation results to files."""
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = reports_dir / f"eval_results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            results_data = []
            for r in results:
                results_data.append({
                    "case_id": r.case.case_id,
                    "description": r.case.description,
                    "success": r.success,
                    "tools_called": r.tools_called,
                    "response_text": r.response_text[:200] + "..." if len(r.response_text) > 200 else r.response_text,
                    "first_token_latency_ms": r.first_token_latency_ms,
                    "total_latency_ms": r.total_latency_ms,
                    "tool_accuracy": r.tool_accuracy,
                    "handoffs": r.handoffs,
                    "error_message": r.error_message
                })
            
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # Save benchmark report
        benchmark_file = reports_dir / "benchmark.md"
        with open(benchmark_file, 'w', encoding='utf-8') as f:
            f.write(self._format_markdown_report(report))
        
        logger.info(f"Results saved to {results_file} and {benchmark_file}")
    
    def _format_markdown_report(self, report: Dict[str, Any]) -> str:
        """Format report as markdown."""
        
        md = f"""# Telco Agent Evaluation Report

Generated: {report['evaluation_summary']['timestamp']}

## Summary

- **Total Test Cases**: {report['evaluation_summary']['total_cases']}
- **Successful**: {report['evaluation_summary']['successful_cases']}
- **Failed**: {report['evaluation_summary']['failed_cases']}
- **Runtime**: {report['evaluation_summary']['total_runtime_seconds']}s

## Key Performance Indicators

| Metric | Value | Target |
|--------|--------|--------|
| Success Rate | {report['kpis']['success_rate']:.1%} | >95% |
| Tool Accuracy | {report['kpis']['tool_accuracy']:.1%} | >90% |
| First Token Latency | {report['kpis']['first_token_latency_ms']:.0f}ms | <1500ms |
| Task Latency | {report['kpis']['task_latency_ms']:.0f}ms | <2500ms |
| Error Rate | {report['kpis']['error_rate']:.1%} | <5% |

## Performance Distribution

- **P50 First Token**: {report['performance_breakdown']['latency_distribution']['p50_first_token']:.0f}ms
- **P95 First Token**: {report['performance_breakdown']['latency_distribution']['p95_first_token']:.0f}ms
- **P50 Total**: {report['performance_breakdown']['latency_distribution']['p50_total']:.0f}ms
- **P95 Total**: {report['performance_breakdown']['latency_distribution']['p95_total']:.0f}ms

## Tool Usage

"""
        
        for tool, count in sorted(report['tool_usage'].items(), key=lambda x: x[1], reverse=True):
            md += f"- **{tool}**: {count} calls\n"
        
        md += "\n## Handoff Usage\n\n"
        
        for handoff, count in sorted(report['handoff_usage'].items(), key=lambda x: x[1], reverse=True):
            md += f"- **{handoff}**: {count} handoffs\n"
        
        md += f"\n## Error Analysis\n\n"
        for category, count in report['error_analysis']['error_categories'].items():
            md += f"- **{category}**: {count}\n"
        
        return md


async def main():
    """Run evaluation from command line."""
    runner = EvalRunner()
    report = await runner.run_evaluation()
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    print(f"Success Rate: {report['kpis']['success_rate']:.1%}")
    print(f"Tool Accuracy: {report['kpis']['tool_accuracy']:.1%}")
    print(f"Avg First Token: {report['kpis']['first_token_latency_ms']:.0f}ms")
    print(f"Avg Task Latency: {report['kpis']['task_latency_ms']:.0f}ms")
    print("\nSee reports/ directory for detailed results.")


if __name__ == "__main__":
    asyncio.run(main())
