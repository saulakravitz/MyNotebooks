#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Generated from FHIR 3.3.0.13671 (http://hl7.org/fhir/StructureDefinition/CodeableConcept) on 2018-12-17.
#  2018, SMART Health IT.

import logging
from . import element


class FHIRPrimitive(element.Element):
    """ FHIR Primitive Class - is just an empty class for now
    """
    
    resource_type = "FHIRPrimitive"
    
    def __init__(self, jsondict=None, strict=True):
        """ Initialize all valid properties.
        
        :raises: FHIRValidationError on validation errors, unless strict is False
        :param dict jsondict: A JSON dictionary to use for initialization
        :param bool strict: If True (the default), invalid variables will raise a TypeError
        """
    
        # setattr(self,sunder_name,None)  # how do I get the name
        
        super(FHIRPrimitive, self).__init__(jsondict=jsondict, strict=strict)
    

    






