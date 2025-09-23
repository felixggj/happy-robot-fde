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
        # Clean MC number (remove MC- prefix if present)
        identifier = mc_number.strip()
        if identifier.upper().startswith("MC"):
            identifier = identifier.replace("MC-", "").replace("MC", "").strip()
        
        url = f"{FMCSA_BASE_URL}/docketNumber/{identifier}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
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
        legal_name = carrier.get("legalName", "Unknown")
        operating_status = carrier.get("operatingStatus", "").upper()
        out_of_service_date = carrier.get("outOfServiceDate")
        
        # Determine eligibility
        eligible = (
            operating_status in ["ACTIVE", "AUTHORIZED"] and
            not out_of_service_date
        )
        
        # Collect risk notes
        risk_notes = []
        if operating_status not in ["ACTIVE", "AUTHORIZED"]:
            risk_notes.append(f"Operating status: {operating_status}")
        if out_of_service_date:
            risk_notes.append(f"Out of service: {out_of_service_date}")
            
        # Check safety rating
        safety_rating = carrier.get("safetyRating", "")
        if safety_rating in ["UNSATISFACTORY"]:
            risk_notes.append(f"Safety rating: {safety_rating}")
            eligible = False
        elif safety_rating in ["CONDITIONAL"]:
            risk_notes.append(f"Safety rating: {safety_rating}")
            
        return {
            "eligible": eligible,
            "legalName": legal_name,
            "status": operating_status.lower(),
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


