import pytest
from unittest import result
import index
import math
import query

def test():
    assert 1+1 == 2

def testIDsToTitles():
    example1 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").ids_to_titles
    exampleDict = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
    assert example1 == exampleDict

def testTitlesToIDS():
    example1 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").titles_to_id
    exampleDict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    assert example1 == exampleDict

def testIsLink():
    example1 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").is_link("[[hello]]")
    assert example1 == True
    example2 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").is_link("[[hello|goodbye]]")
    assert example2 == True
    example3 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").is_link("hello")
    assert example3 == False

def testSplitLink():
    example1 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").split_link("[[hello]]")
    assert example1 == (['hello'], 'hello')
    example2 = index.Indexer("wikis/testProcessingEx1.xml","titles.xml","docs.xml","words.xml").split_link("[[hello|goodbye]]")
    assert example2 == (['goodbye'], 'hello')

def testRelevance():
    example1 = index.Indexer("wikis/example4.xml","titles.xml","docs.xml","words.xml")
    relevance = example1.relevance
    assert relevance['theater'][0] == 0.0
    assert relevance['theater'][1] == 0.0
    assert relevance['theater'][2] == 0.0
    expectedValue1 = math.log(3/2) * 1/2
    assert relevance['dog'][0] == pytest.approx(expectedValue1, 0.1)
    expectedValue2 = math.log(3/2) 
    assert relevance['dog'][1] == pytest.approx(expectedValue2, 0.1)
    assert relevance['bit'][0] == pytest.approx(expectedValue1, 0.1)
    assert relevance['bit'][2] == pytest.approx(expectedValue1, 0.1)
    expectedValue3 = math.log(3) * 1/2
    assert relevance['man'][0] == pytest.approx(expectedValue3, 0.1)
    expectedValue4 = math.log(3) * 1
    assert relevance['ate'][1] == pytest.approx(expectedValue4, 0.1)
    assert relevance['chees'][1] == pytest.approx(expectedValue2, 0.1)
    assert relevance['chees'][2] == pytest.approx(expectedValue2, 0.1)


def testPageRank():
    example1 = index.Indexer("wikis/SmallWiki.xml","titles.xml","docs.xml","words.xml")
    page_weight = example1.r_prime
    values1 = page_weight.values()
    total1 = sum(values1)
    expectedValue = 1
    assert total1 == pytest.approx(expectedValue, 0.1)
    
    example2 = index.Indexer("wikis/PageRankExample1.xml","titles.xml","docs.xml","words.xml")
    page_weight = example2.r_prime
    values2 = page_weight.values()
    total2 = sum(values2)
    assert total2 == pytest.approx(expectedValue, 0.1)

    example3 = index.Indexer("wikis/PageRankExample2.xml","titles.xml","docs.xml","words.xml")
    page_weight = example3.r_prime
    values3 = page_weight.values()
    total3 = sum(values3)
    assert total3 == pytest.approx(expectedValue, 0.1)
