"""Pytest setup"""
from os.path import dirname, join

from pytest import fixture
from xmlschema import XMLSchema


@fixture(scope="session")
def feature_definition_xml_schema() -> XMLSchema:
    return XMLSchema(join(dirname(__file__), "..", "..", "resources", "xsd", "FeatureDefinition.xsd"))
