#!/usr/bin/env python3
"""
Comprehensive Application Test Script
Tests all endpoints and features of the AstroBiomers application
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style
init(autoreset=True)

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

class ApplicationTester:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def log_test(self, name, status, message=""):
        """Log test result"""
        self.results["tests"].append({
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if status == "PASS":
            self.results["passed"] += 1
            print(f"{Fore.GREEN}✓ PASS{Style.RESET_ALL} - {name}")
            if message:
                print(f"  {Fore.CYAN}{message}{Style.RESET_ALL}")
        else:
            self.results["failed"] += 1
            print(f"{Fore.RED}✗ FAIL{Style.RESET_ALL} - {name}")
            if message:
                print(f"  {Fore.YELLOW}{message}{Style.RESET_ALL}")
    
    def test_server_health(self):
        """Test if servers are running"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}1. SERVER HEALTH CHECKS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        # Test Backend
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Server Health", "PASS", f"Status: {response.json()}")
            else:
                self.log_test("Backend Server Health", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Server Health", "FAIL", f"Error: {str(e)}")
        
        # Test Frontend
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Server", "PASS", f"Accessible at {FRONTEND_URL}")
            else:
                self.log_test("Frontend Server", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Server", "FAIL", f"Error: {str(e)}")
    
    def test_knowledge_graph(self):
        """Test Knowledge Graph API"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}2. KNOWLEDGE GRAPH TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        # Test search
        test_queries = ["stem cells", "microgravity", "mars", "bacteria"]
        
        for query in test_queries:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/api/knowledge-graph",
                    params={"q": query},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    node_count = len(data.get("nodes", []))
                    edge_count = len(data.get("edges", []))
                    self.log_test(
                        f"Knowledge Graph Search: '{query}'",
                        "PASS",
                        f"Found {node_count} nodes, {edge_count} edges"
                    )
                else:
                    self.log_test(
                        f"Knowledge Graph Search: '{query}'",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    f"Knowledge Graph Search: '{query}'",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def test_paper_endpoints(self):
        """Test paper retrieval"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}3. PAPER ENDPOINT TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        # First get some paper IDs from knowledge graph
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/knowledge-graph",
                params={"q": "stem cells"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                papers = [n for n in data.get("nodes", []) if n.get("type") == "paper"]
                
                if papers:
                    # Test first few papers
                    for paper in papers[:3]:
                        paper_id = paper.get("paperId") or paper.get("id")
                        if paper_id:
                            try:
                                paper_response = requests.get(
                                    f"{BACKEND_URL}/api/paper/{paper_id}",
                                    timeout=10
                                )
                                if paper_response.status_code == 200:
                                    paper_data = paper_response.json()
                                    self.log_test(
                                        f"Paper Details: {paper_id}",
                                        "PASS",
                                        f"Title: {paper_data.get('title', 'N/A')[:50]}..."
                                    )
                                else:
                                    self.log_test(
                                        f"Paper Details: {paper_id}",
                                        "FAIL",
                                        f"Status: {paper_response.status_code}"
                                    )
                            except Exception as e:
                                self.log_test(
                                    f"Paper Details: {paper_id}",
                                    "FAIL",
                                    f"Error: {str(e)}"
                                )
                else:
                    self.log_test("Paper Endpoints", "FAIL", "No papers found in graph")
        except Exception as e:
            self.log_test("Paper Endpoints", "FAIL", f"Error: {str(e)}")
    
    def test_search_endpoint(self):
        """Test search functionality"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}4. SEARCH ENDPOINT TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        search_terms = ["microgravity", "stem cells", "space biology", "ISS"]
        
        for term in search_terms:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/api/search",
                    params={"q": term},
                    timeout=10
                )
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results.get("results", []))
                    self.log_test(
                        f"Search: '{term}'",
                        "PASS",
                        f"Found {result_count} results"
                    )
                else:
                    self.log_test(
                        f"Search: '{term}'",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    f"Search: '{term}'",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def test_ai_chat(self):
        """Test AI Chat endpoint"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}5. AI CHAT TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        test_questions = [
            "What are the effects of microgravity on stem cells?",
            "Tell me about space biology research"
        ]
        
        for question in test_questions:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={"message": question},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    self.log_test(
                        f"AI Chat: '{question[:40]}...'",
                        "PASS",
                        f"Response length: {len(response_text)} chars"
                    )
                else:
                    self.log_test(
                        f"AI Chat: '{question[:40]}...'",
                        "FAIL",
                        f"Status: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    f"AI Chat: '{question[:40]}...'",
                    "FAIL",
                    f"Error: {str(e)}"
                )
    
    def test_database_connection(self):
        """Test database connectivity"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}6. DATABASE CONNECTION TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/knowledge-graph",
                params={"q": "test"},
                timeout=10
            )
            if response.status_code == 200:
                self.log_test(
                    "Neo4j Database Connection",
                    "PASS",
                    "Successfully queried knowledge graph"
                )
            else:
                self.log_test(
                    "Neo4j Database Connection",
                    "FAIL",
                    f"Could not query database: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Neo4j Database Connection",
                "FAIL",
                f"Error: {str(e)}"
            )
    
    def test_cors_headers(self):
        """Test CORS configuration"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}7. CORS CONFIGURATION TESTS{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        try:
            response = requests.options(
                f"{BACKEND_URL}/api/knowledge-graph",
                headers={
                    "Origin": "http://localhost:8080",
                    "Access-Control-Request-Method": "GET"
                },
                timeout=5
            )
            
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers:
                self.log_test(
                    "CORS Configuration",
                    "PASS",
                    f"Allow-Origin: {cors_headers}"
                )
            else:
                self.log_test(
                    "CORS Configuration",
                    "FAIL",
                    "No CORS headers found"
                )
        except Exception as e:
            self.log_test(
                "CORS Configuration",
                "FAIL",
                f"Error: {str(e)}"
            )
    
    def generate_report(self):
        """Generate final test report"""
        print(f"\n{Fore.BLUE}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}TEST SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}\n")
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {self.results['passed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.results['failed']}{Style.RESET_ALL}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Save detailed report
        report_file = "test_results.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Fore.CYAN}Detailed report saved to: {report_file}{Style.RESET_ALL}")
        
        if pass_rate == 100:
            print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED! Application is fully functional!{Style.RESET_ALL}")
        elif pass_rate >= 80:
            print(f"\n{Fore.YELLOW}⚠️  Most tests passed, but some issues need attention{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Multiple failures detected. Please review the issues above{Style.RESET_ALL}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}ASTROBIOMERS - COMPREHENSIVE APPLICATION TEST{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")
        
        self.test_server_health()
        self.test_knowledge_graph()
        self.test_paper_endpoints()
        self.test_search_endpoint()
        self.test_ai_chat()
        self.test_database_connection()
        self.test_cors_headers()
        
        self.generate_report()

if __name__ == "__main__":
    tester = ApplicationTester()
    tester.run_all_tests()
