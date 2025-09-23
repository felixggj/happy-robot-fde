"""FMCSA carrier verification client."""
import os
from typing import Optional, List, Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)

FMCSA_WEBKEY = os.getenv("FMCSA_WEBKEY")
FMCSA_BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services/carriers"


async def verify_carrier(mc_number: str) -> Dict[str, Any]:
    """
    Verify carrier eligibility with FMCSA API using MC number.
    
    Args:
        mc_number: Motor Carrier number (MC-123456 or just 123456)
        
    Returns:
        Dict containing eligibility status, legal name, and risk notes
    """
    if not mc_number:
        return {
            "eligible": False,
            "legalName": None,
            "status": "invalid",
            "riskNotes": ["MC number is required"]
        }

    if not FMCSA_WEBKEY:
        logger.warning("FMCSA_WEBKEY not configured, using fallback verification")
        return _fallback_verification(mc_number)

    try:
        # Extract digits only from MC number
        mc_digits = "".join(filter(str.isdigit, mc_number))
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{FMCSA_BASE_URL}/docket-number/{mc_digits}",
                params={"webKey": FMCSA_WEBKEY},
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                return _parse_fmcsa_response(response.json())
            elif response.status_code == 404:
                return {
                    "eligible": False,
                    "legalName": None,
                    "status": "not_found",
                    "riskNotes": ["Carrier not found in FMCSA database"]
                }
            else:
                logger.error(f"FMCSA API error: {response.status_code} - {response.text}")
                return _fallback_verification(mc_number)
                
    except httpx.TimeoutException:
        logger.error("FMCSA API timeout")
        return _fallback_verification(mc_number)
    except Exception as e:
        logger.error(f"FMCSA API error: {str(e)}")
        return _fallback_verification(mc_number)


def _parse_fmcsa_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse FMCSA API response and extract relevant information."""
    try:
        content = data.get("content", [])
        if not content:
            return {
                "eligible": False,
                "legalName": None,
                "status": "not_found",
                "riskNotes": ["No carrier data found"]
            }
        
        carrier = content[0]  # Take first result
        
        # Extract key information
        legal_name = carrier.get("legalName")
        dot_number = carrier.get("dotNumber")
        allow_to_operate = carrier.get("allowToOperate") == "Y"
        out_of_service = carrier.get("outOfService")
        
        # Determine eligibility based on official flags
        eligible = allow_to_operate and not out_of_service
        
        # Collect risk notes
        risk_notes = []
        if not allow_to_operate:
            risk_notes.append("Not allowed to operate")
        if out_of_service:
            risk_notes.append("Out of service")
            
        return {
            "eligible": eligible,
            "legalName": legal_name,
            "status": "active" if eligible else "inactive",
            "riskNotes": risk_notes
        }
        
    except Exception as e:
        logger.error(f"Error parsing FMCSA response: {str(e)}")
        return {
            "eligible": False,
            "legalName": None,
            "status": "error",
            "riskNotes": ["Error processing carrier data"]
        }


def _fallback_verification(mc_number: str) -> Dict[str, Any]:
    """Fallback when FMCSA API is unavailable - returns error for production safety."""
    logger.error("FMCSA API unavailable and no fallback configured for production")
    
    return {
        "eligible": False,
        "legalName": None,
        "status": "error",
        "riskNotes": ["Carrier verification unavailable - please try again later"]
    }


