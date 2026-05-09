# Telecom Trace Analysis Report

## Procedure identified

**5G Initial Registration** (3GPP access via NR)

This trace captures a complete initial registration procedure for a UE attaching to a 5G standalone (SA) network through an NR cell. The procedure includes authentication, NAS security establishment, and initial context setup across the NG interface.

## Technical summary

The UE initiated a registration procedure from an unregistered state, presenting a SUCI for privacy-preserving identification. The AMF performed 5G-AKA authentication using EAP-AKA' challenge-response, followed by NAS security mode establishment with 128-bit encryption and integrity algorithms. The AMF assigned a 5G-GUTI, configured tracking area lists, and granted access to the requested network slice (SST=1, SD=0x010203). The gNB successfully established the initial AS context, and the UE confirmed registration completion.

## Observed signaling flow

1. **Initial UE Message (NGAP)**: gNB forwarded the UE's registration attempt to AMF, carrying RAN UE NGAP ID 0x00001001, cell location (NR Cell ID 0xABCDE12345, TAC 0x00A1, PLMN 001-01), and the encapsulated NAS Registration Request.

2. **Registration Request (NAS)**: UE requested initial registration with SUCI (MCC=001, MNC=01, MSIN=1234567890), ngKSI marked as "Not Available" (indicating no prior security context), UE security capabilities (128-NEA1/2, 128-NIA1/2), and requested NSSAI (SST=1, SD=0x010203).

3. **Authentication Request (NAS)**: AMF initiated 5G-AKA authentication with ngKSI=0x01, RAND (0x8F3A2B1C4D5E6F708192AABBCCDDEEFF), AUTN (0x11223344556677889900AABBCCDDEEFF), and ABBA parameter (0x0000).

4. **Authentication Response (NAS)**: UE returned RES* (0xA1B2C3D4E5F60708), demonstrating successful USIM authentication and derivation of the anchor key KAUSF.

5. **Security Mode Command (NAS)**: AMF selected 128-NEA2 for ciphering and 128-NIA2 for integrity protection, referencing ngKSI=0x01 to bind the security context.

6. **Security Mode Complete (NAS)**: UE confirmed security activation and provided IMEISV (356789012345678) for equipment identification. This message was integrity-protected and ciphered using the newly established NAS security context.

7. **Initial Context Setup Request (NGAP)**: AMF instructed gNB to establish the initial UE context, assigning AMF UE NGAP ID 0x00002001, and encapsulating the Registration Accept message.

8. **Registration Accept (NAS)**: AMF assigned a 5G-GUTI (specific value not visible in trace), provided TAI list (TAC 0x00A1, 0x00A2), granted allowed NSSAI (SST=1, SD=0x010203), and configured periodic registration timer T3512=3600s and registration retry timer T3502=720s.

9. **Initial Context Setup Response (NGAP)**: gNB confirmed successful context establishment, correlating AMF UE NGAP ID 0x00002001 with RAN UE NGAP ID 0x00001001.

10. **Registration Complete (NAS)**: UE acknowledged successful registration, completing the procedure.

## Key protocol phases

### Phase 1: Initial UE Message and Registration Request
- **NGAP layer**: gNB relayed the initial NAS message with RAN-side identifiers and cell location information.
- **NAS layer**: UE presented SUCI for privacy, declared no existing security context (ngKSI unavailable), and requested specific network slice.

### Phase 2: Authentication
- AMF challenged the UE using 5G-AKA with RAND/AUTN parameters.
- UE validated AUTN (confirming network authenticity) and computed RES* from USIM credentials.
- Successful authentication enabled derivation of KSEAF at both UE and AMF.

### Phase 3: Security Mode Establishment
- AMF selected NAS security algorithms from UE's declared capabilities.
- UE activated NAS security and confirmed with integrity-protected response.
- IMEISV disclosure occurred after security activation, protecting equipment identity.

### Phase 4: Initial Context Setup
- AMF triggered AS-level context establishment via NGAP.
- Registration Accept was delivered within the NGAP Initial Context Setup Request.
- gNB allocated radio resources and confirmed readiness.

### Phase 5: Registration Completion
- UE sent Registration Complete to finalize the procedure.
- UE transitioned to RM-REGISTERED and CM-CONNECTED states.

## Cross-layer observations

**NAS-NGAP encapsulation**: NAS messages (Registration Request, Registration Accept) were transported as NAS-PDU information elements within NGAP messages (Initial UE Message, Initial Context Setup Request). This demonstrates the standard NG interface architecture where NAS signaling is transparently relayed through the RAN.

**Identifier correlation**: The NGAP layer established bidirectional identifier mapping (RAN UE NGAP ID 0x00001001 ↔ AMF UE NGAP ID 0x00002001) before NAS-level registration completion. This enabled subsequent NGAP procedures to reference the correct UE context.

**Security domain separation**: NAS security (128-NEA2/NIA2) was established independently of AS security. The Security Mode Complete message, which carries IMEISV, was the first NAS message transmitted under integrity protection and ciphering.

**Context synchronization**: The Initial Context Setup Request served dual purposes: establishing AS-level security context at the gNB and delivering the Registration Accept to the UE. This ensures the gNB has necessary context (security keys, QoS parameters) before the UE considers itself registered.

## Security context observations

**Authentication method**: 5G-AKA was employed with RAND/AUTN challenge and RES* response. The ABBA parameter (0x0000) indicates no anti-bidding-down protection was required, consistent with initial registration from an unregistered state.

**Key hierarchy**: The ngKSI value 0x01 was assigned during authentication and referenced in Security Mode Command, binding the NAS security context to the authentication event. This enables derivation of KNAS_enc and KNAS_int from KSEAF.

**Algorithm selection**: AMF selected 128-NEA2 (128-bit AES-based encryption) and 128-NIA2 (128-bit AES-based integrity) from the UE's offered capabilities (NEA1/2, NIA1/2). The selection of NEA2/NIA2 indicates preference for AES-based algorithms over SNOW 3G variants.

**SUCI-to-GUTI transition**: The UE initially identified with SUCI (concealed SUPI using public key encryption), and the AMF assigned a 5G-GUTI after successful authentication. This transition protects subscriber permanent identity from exposure on the radio interface.

**IMEISV protection**: The IMEISV was transmitted only after NAS security activation, preventing passive interception of equipment identity.

## Potential gaps or anomalies

**5G-GUTI value not captured**: The trace indicates a 5G-GUTI was assigned in Registration Accept but does not show the specific value. This limits the ability to track subsequent procedures using this temporary identity.

**No PDU Session Establishment**: The trace terminates after registration completion without any PDU Session Establishment Request. The UE is registered but has no user-plane connectivity. This may be intentional (signaling-only registration) or the trace may be incomplete.

**Single NSSAI granted**: The UE requested SST=1, SD=0x010203, and this was granted as the allowed NSSAI. No rejected NSSAI or additional slices are visible, suggesting either exact match or limited slice configuration.

**TAI list limited to two TACs**: The Registration Accept provided only two TACs (0x00A1, 0x00A2) in the TAI list. This may indicate a small tracking area configuration or a truncated list in the trace.

**No UE capability information**: The trace does not show NGAP UE Radio Capability Info Transfer or NAS UE Radio Capability ID procedures. The network may not have requested detailed UE capabilities during this registration.

## Baseline specification compatibility

**Minimum 3GPP Release: Release 15**

The observed features align with 3GPP Release 15 (first 5G SA release):

- **SUCI-based privacy**: TS 33.501 Release 15 introduced SUCI for concealing SUPI.
- **5G-AKA authentication**: TS 33.501 Release 15 defined 5G-AKA with RAND/AUTN/RES*.
- **NAS security algorithms**: 128-NEA2 and 128-NIA2 were specified in TS 33.501 Release 15.
- **Network slicing**: NSSAI with SST and SD was introduced in Release 15 (TS 23.501).
- **NG interface procedures**: NGAP Initial UE Message and Initial Context Setup Request are core Release 15 procedures (TS 38.413).

No features requiring Release 16 or later (e.g., NSAG, URSP, enhanced slicing) are evident in this trace. The procedure is consistent with baseline 5G SA functionality as standardized in Release 15.

**Note**: This assessment identifies the minimum release required to support the observed features. It does not determine the actual release deployed in the network, which may be later.

## Suggested next checks

1. **Verify 5G-GUTI assignment**: Capture the complete Registration Accept message to confirm the 5G-GUTI structure (GUAMI + 5G-TMSI) and validate proper temporary identity allocation.

2. **Trace PDU Session Establishment**: Extend the capture to include PDU Session Establishment Request/Accept to verify user-plane setup, QoS flow configuration, and DNN assignment.

3. **Validate AS security**: Capture RRC Security Mode Command/Complete to confirm AS-level algorithm selection (NEA/NIA for RRC and UP) and verify consistency with NAS security choices.

4. **Check AUSF/UDM interactions**: If possible, capture N12 (AMF-AUSF) and N8 (AUSF-UDM) interfaces to verify authentication vector retrieval and SUPI de-concealment.

5. **Test mobility procedures**: Trigger intra-AMF handover or registration update to verify TAI list usage and mobility management timer behavior (T3512 periodic registration).

6. **Examine slice rejection handling**: Attempt registration with unsupported NSSAI values to verify rejected NSSAI signaling and UE behavior.

7. **Verify UE capability exchange**: Check if UE Radio Capability Info Transfer occurs during or after registration, particularly before PDU session establishment.

8. **Analyze timer configurations**: Monitor T3512 (3600s) and T3502 (720s) expiry to confirm periodic registration and retry behavior align with network policy.

9. **Test de-registration scenarios**: Initiate UE-originated or network-initiated de-registration to verify context release procedures and NGAP UE Context Release signaling.

10. **Validate PLMN/TAC consistency**: Cross-reference the observed PLMN (001-01) and TACs (0x00A1, 0x00A2) with network planning documents to ensure correct cell configuration.