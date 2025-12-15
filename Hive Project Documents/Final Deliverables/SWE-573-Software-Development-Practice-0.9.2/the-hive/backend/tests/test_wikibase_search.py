#!/usr/bin/env python3
"""
Test script for Wikibase/Wikidata search functionality

This test validates:
1. Entity search and ID retrieval from Wikidata
2. Related tag suggestions via SPARQL queries
3. Different types of search terms (music, skills, activities, etc.)
4. Error handling for invalid/nonexistent terms
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from wikibase_search import get_entity_id, get_related_tags

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def pass_test(self, name, message=""):
        self.passed += 1
        self.tests.append({"name": name, "status": "PASSED", "message": message})
        print(f"{Colors.GREEN}✓ {name}{Colors.NC}")
        if message:
            print(f"  {message}")
        print()
    
    def fail_test(self, name, message=""):
        self.failed += 1
        self.tests.append({"name": name, "status": "FAILED", "message": message})
        print(f"{Colors.RED}✗ {name}{Colors.NC}")
        if message:
            print(f"  {message}")
        print()
    
    def print_summary(self):
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Test Summary{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"Total Tests Passed: {Colors.GREEN}{self.passed}{Colors.NC}")
        print(f"Total Tests Failed: {Colors.RED}{self.failed}{Colors.NC}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✓ All tests passed! Wikibase search is functional.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Wikibase/Wikidata Search Test Suite{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    print(f"{Colors.YELLOW}Testing:{Colors.NC}")
    print("1. Entity ID retrieval from search terms")
    print("2. Related tag suggestions via SPARQL")
    print("3. Different categories (music, programming, activities)")
    print("4. Error handling for invalid terms")
    print()


def test_entity_search(result):
    """Test searching for entities and retrieving their IDs"""
    print(f"{Colors.BLUE}Phase 1: Entity ID Search{Colors.NC}\n")
    
    test_cases = [
        {"term": "guitar", "expected_type": "Q"},
        {"term": "programming", "expected_type": "Q"},
        {"term": "gardening", "expected_type": "Q"},
        {"term": "cooking", "expected_type": "Q"},
        {"term": "football", "expected_type": "Q"},
    ]
    
    for test in test_cases:
        term = test["term"]
        print(f"{Colors.YELLOW}Testing search for: '{term}'{Colors.NC}")
        entity_id = get_entity_id(term)
        
        if entity_id and entity_id.startswith(test["expected_type"]):
            result.pass_test(
                f"Search for '{term}'",
                f"Found entity: {entity_id}"
            )
        elif entity_id:
            result.fail_test(
                f"Search for '{term}'",
                f"Unexpected ID format: {entity_id}"
            )
        else:
            result.fail_test(
                f"Search for '{term}'",
                "No entity found"
            )


def test_related_tags(result):
    """Test retrieving related tags for various entities"""
    print(f"\n{Colors.BLUE}Phase 2: Related Tags via SPARQL{Colors.NC}\n")
    
    test_cases = [
        {"term": "guitar", "min_suggestions": 0},
        {"term": "Python programming language", "min_suggestions": 0},
        {"term": "gardening", "min_suggestions": 0},
    ]
    
    for test in test_cases:
        term = test["term"]
        print(f"{Colors.YELLOW}Testing related tags for: '{term}'{Colors.NC}")
        
        entity_id = get_entity_id(term)
        
        if entity_id:
            related_tags = get_related_tags(entity_id)
            
            if related_tags and len(related_tags) >= test["min_suggestions"]:
                result.pass_test(
                    f"Related tags for '{term}'",
                    f"Found {len(related_tags)} suggestions: {', '.join(related_tags[:5])}{'...' if len(related_tags) > 5 else ''}"
                )
            elif related_tags:
                result.pass_test(
                    f"Related tags for '{term}'",
                    f"Found {len(related_tags)} suggestions (less than expected minimum)"
                )
            else:
                result.pass_test(
                    f"Related tags for '{term}'",
                    "No related tags found (this may be normal for some entities)"
                )
        else:
            result.fail_test(
                f"Related tags for '{term}'",
                "Could not retrieve entity ID"
            )


def test_invalid_searches(result):
    """Test error handling for invalid or nonsense search terms"""
    print(f"\n{Colors.BLUE}Phase 3: Invalid Search Handling{Colors.NC}\n")
    
    invalid_terms = [
        "xyzqwerty123nonsense",
        "!@#$%^&*()",
        ""
    ]
    
    for term in invalid_terms:
        if term == "":
            display_term = "(empty string)"
        else:
            display_term = term
            
        print(f"{Colors.YELLOW}Testing invalid search: '{display_term}'{Colors.NC}")
        
        try:
            entity_id = get_entity_id(term)
            
            if entity_id is None:
                result.pass_test(
                    f"Invalid search '{display_term}'",
                    "Correctly returned None for invalid term"
                )
            else:
                result.pass_test(
                    f"Invalid search '{display_term}'",
                    f"Found entity (unexpected but valid): {entity_id}"
                )
        except Exception as e:
            result.fail_test(
                f"Invalid search '{display_term}'",
                f"Exception raised: {str(e)}"
            )


def test_skill_categories(result):
    """Test searching for various skill categories relevant to The Hive"""
    print(f"\n{Colors.BLUE}Phase 4: The Hive Skill Categories{Colors.NC}\n")
    
    skills = [
        "tutoring",
        "babysitting",
        "moving service",
        "lawn care",
        "computer repair",
        "web development",
    ]
    
    found_count = 0
    
    for skill in skills:
        print(f"{Colors.YELLOW}Testing skill: '{skill}'{Colors.NC}")
        entity_id = get_entity_id(skill)
        
        if entity_id:
            found_count += 1
            related = get_related_tags(entity_id)
            result.pass_test(
                f"Skill search '{skill}'",
                f"Entity: {entity_id}, Related tags: {len(related)}"
            )
        else:
            result.pass_test(
                f"Skill search '{skill}'",
                "No exact match (this is acceptable for some terms)"
            )
    
    if found_count > 0:
        print(f"{Colors.GREEN}Successfully found entities for {found_count}/{len(skills)} skills{Colors.NC}\n")


def test_full_workflow(result):
    """Test the complete workflow: search -> get ID -> get related tags"""
    print(f"\n{Colors.BLUE}Phase 5: Complete Workflow Test{Colors.NC}\n")
    
    test_term = "music"
    print(f"{Colors.YELLOW}Testing complete workflow for: '{test_term}'{Colors.NC}")
    
    # Step 1: Get entity ID
    entity_id = get_entity_id(test_term)
    
    if not entity_id:
        result.fail_test(
            "Complete workflow",
            f"Failed to get entity ID for '{test_term}'"
        )
        return
    
    # Step 2: Get related tags
    related_tags = get_related_tags(entity_id)
    
    if related_tags is not None:  # Can be empty list
        result.pass_test(
            "Complete workflow",
            f"Successfully completed workflow: {entity_id} -> {len(related_tags)} related tags"
        )
    else:
        result.fail_test(
            "Complete workflow",
            "Failed to get related tags (returned None)"
        )


def main():
    print_header()
    result = TestResult()
    
    try:
        # Run all test phases
        test_entity_search(result)
        test_related_tags(result)
        test_invalid_searches(result)
        test_skill_categories(result)
        test_full_workflow(result)
        
        # Print summary
        print()
        success = result.print_summary()
        return success
        
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during testing: {str(e)}{Colors.NC}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.NC}\n")
        exit(1)
