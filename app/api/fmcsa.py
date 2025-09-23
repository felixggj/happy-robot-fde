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
    logger.info(f"Starting carrier verification for MC number: {mc_number}")
    
    if not mc_number:
        logger.warning("MC number is empty or None")
        return {
            "eligible": False,
            "legalName": None,
            "status": "invalid",
            "riskNotes": ["MC number is required"]
        }

    if not FMCSA_WEBKEY:
        logger.error("FMCSA_WEBKEY environment variable not configured")
        return _fallback_verification(mc_number)

    try:
        # Extract digits only from MC number
        mc_digits = "".join(filter(str.isdigit, mc_number))
        logger.info(f"Extracted MC digits: {mc_digits} from input: {mc_number}")
        
        # Build request details
        url = f"{FMCSA_BASE_URL}/docket-number/{mc_digits}"
        params = {"webKey": FMCSA_WEBKEY}
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        }
        
        logger.info(f"Making FMCSA API request:")
        logger.info(f"  URL: {url}")
        logger.info(f"  Params: webKey={FMCSA_WEBKEY[:10]}..." if FMCSA_WEBKEY else "  Params: webKey=None")
        logger.info(f"  Headers: {headers}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            
            logger.info(f"FMCSA API Response:")
            logger.info(f"  Status Code: {response.status_code}")
            logger.info(f"  Response Headers: {dict(response.headers)}")
            logger.info(f"  Response Text (first 500 chars): {response.text[:500]}")
            logger.info(f"  Request URL: {response.url}")
            logger.info(f"  Request Headers: {dict(response.request.headers)}")
            
            if response.status_code == 200:
                logger.info("FMCSA API request successful, parsing response")
                json_response = response.json()
                logger.info(f"FMCSA JSON Response: {json_response}")
                return _parse_fmcsa_response(json_response)
            elif response.status_code == 404:
                logger.warning(f"Carrier {mc_digits} not found in FMCSA database")
                return {
                    "eligible": False,
                    "legalName": None,
                    "status": "not_found",
                    "riskNotes": ["Carrier not found in FMCSA database"]
                }
            else:
                logger.error(f"FMCSA API error: {response.status_code}")
                logger.error(f"Full response text: {response.text}")
                logger.error(f"Response headers: {dict(response.headers)}")
                return _fallback_verification(mc_number)
                
    except httpx.TimeoutException as e:
        logger.error(f"FMCSA API timeout: {str(e)}")
        return _fallback_verification(mc_number)
    except Exception as e:
        logger.error(f"FMCSA API unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return _fallback_verification(mc_number)


def _parse_fmcsa_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse FMCSA API response and extract relevant information."""
    try:
        logger.info(f"Parsing FMCSA response data: {data}")
        
        content = data.get("content", [])
        if not content:
            logger.warning("No content found in FMCSA response")
            return {
                "eligible": False,
                "legalName": None,
                "status": "not_found",
                "riskNotes": ["No carrier data found"]
            }
        
        logger.info(f"Found {len(content)} content items")
        carrier_data = content[0].get("carrier", {}) 
        logger.info(f"Carrier data extracted: {carrier_data}")
        
        # Extract key information
        legal_name = carrier_data.get("legalName")
        dot_number = carrier_data.get("dotNumber")
        allow_to_operate = carrier_data.get("allowedToOperate") == "Y"
        out_of_service = carrier_data.get("oosDate") is not None
        
        logger.info(f"Parsed values:")
        logger.info(f"  Legal Name: {legal_name}")
        logger.info(f"  DOT Number: {dot_number}")
        logger.info(f"  Allowed to Operate: {carrier_data.get('allowedToOperate')} -> {allow_to_operate}")
        logger.info(f"  OOS Date: {carrier_data.get('oosDate')} -> Out of Service: {out_of_service}")
        
        # Determine eligibility based on official flags
        eligible = allow_to_operate and not out_of_service
        logger.info(f"Final eligibility: {eligible}")
        
        # Collect risk notes
        risk_notes = []
        if not allow_to_operate:
            risk_notes.append("Not allowed to operate")
        if out_of_service:
            risk_notes.append("Out of service")
            
        result = {
            "eligible": eligible,
            "legalName": legal_name,
            "status": "active" if eligible else "inactive",
            "riskNotes": risk_notes
        }
        logger.info(f"Returning parsed result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing FMCSA response: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Raw data that caused error: {data}")
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


