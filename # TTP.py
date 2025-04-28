# TTP.py
def GenZKPoK(params, prev_params, prev_vcerts, all_enc_attr, comm):
    # params: Tuple containing base field/curve info (FQ, FQ2, FQ12), generator G1, order o, hash generators hs for this CA.
    # prev_params: List of params tuples for dependency CAs.
    # prev_vcerts: List of (Commitment_Point, Signature) tuples for dependency Vcerts.
    # all_enc_attr: List of lists. Outer list corresponds to [dep1_attrs, dep2_attrs, ..., current_attrs].
    #               Inner list contains encoded attribute values for that Vcert, INCLUDING sk_u (at index 0) and r (at index -1).
    # comm: The Commitment_Point 'C' for the *current* Vcert request being proven.

    _, g, o, hs= params # Unpack current CA parameters (g=G1, o=curve_order, hs=hash generators H_j for attributes)

    # --- Step 1: Commitment Generation ---
    # Choose random witnesses (w in Schnorr) for *all* secret attributes across *all* relevant Vcerts (current + dependencies).
    # The structure mirrors `all_enc_attr`.
    total_wm = [[random.randint(2, o) for _ in range(len(all_enc_attr[i]))] for i in range(len(all_enc_attr))]

    # Crucial Link: Ensure the witness for sk_u is the SAME across all proofs if dependencies exist.
    # The secret key sk_u is assumed to be at index 0 in each inner list of all_enc_attr.
    for i in range(1, len(total_wm)):
        total_wm[i][0] = total_wm[0][0] # Use the same random witness for sk_u (index 0)

    # Calculate the commitment points (A = wG in Schnorr) based on the witnesses 'wm' and the *parameters* of each relevant CA.
    Aw = [] # List to store commitment points for each (dependency + current) Vcert context
    comm_list = [] # List to store the actual public commitments corresponding to Aw points

    # Loop through dependency Vcerts
    for i in range(len(prev_vcerts)):
        (_, ttp_g, _, ttp_hs) = prev_params[i] # Get params (generators) for the i-th dependency CA
        # Calculate commitment point: tmp = wm_r * g + sum(wm_j * h_j) + wm_sk * h_sk (implicitly h_sk=h_0)
        tmp = multiply(ttp_g, total_wm[i][-1]) # Start with witness for randomness 'r' * G1
        for j in range(len(total_wm[i]) - 1): # Loop through witnesses for attributes (including sk_u at index 0)
            tmp = add(tmp, multiply(ttp_hs[j], total_wm[i][j])) # Add witness_j * H_j
        Aw.append(tmp) # Store the calculated commitment point for this dependency
        comm_list.append(prev_vcerts[i][0]) # Store the corresponding public commitment C from the Vcert

    # Calculate commitment point for the *current* Vcert request
    # Note: Assumes sk_u is at index 0, r is at index -1 (or len(hs)) in all_enc_attr[len(prev_vcerts)]
    _tmp = multiply(g, total_wm[len(prev_vcerts)][-1]) # Start with witness for randomness 'r' * G1 (current CA's G1)
    # Assuming sk_u is handled by hs[0] implicitly based on Pedersen commitment structure
    # This loop likely covers attributes a_1 to a_q, using hs[1] to hs[q]. Need confirmation on hs structure vs attributes.
    # If sk_u maps to hs[0]:
    _tmp = add(_tmp, multiply(hs[0], total_wm[len(prev_vcerts)][0])) # Add witness_sk * H_0 (assuming H_0 for sk_u)
    # Add commitments for other attributes a_1...a_q (assuming they map to hs[1]...hs[q])
    # The original code had a loop from hs[1] which seemed incorrect; let's assume the loop covers all needed attributes.
    for j in range(1, len(hs)): # Loop through remaining attributes (a_1..a_q if hs=[H_sk, H_a1..H_aq])
         _tmp = add(_tmp, multiply(hs[j], total_wm[len(prev_vcerts)][j])) # Add witness_j * H_j

    # Add other attribute commitments (adjust loop based on actual hs vs attribute mapping)
    # for j in range(1, len(total_wm[len(prev_vcerts)]) - 1): # Original code structure, might need adjustment
    #     _tmp = add(_tmp, multiply(hs[j-1], total_wm[len(prev_vcerts)][j])) # Indices seem offset here if hs[0] is not for sk_u

    Aw.append(_tmp) # Store the calculated commitment point for the current request
    comm_list.append(comm) # Store the corresponding public commitment C for the current request

    # --- Step 2: Challenge Generation (Fiat-Shamir) ---
    # Prepare list of public elements to be hashed for the challenge
    # Includes base generator G1, all commitment points Aw, all public commitments C (comm_list), and public hash generators hs
    element_list = [g] + Aw + comm_list + hs
    c = toChallenge(element_list) % o # Hash the list and reduce modulo curve order 'o'

    # --- Step 3: Response Generation ---
    # Calculate responses r = w - c*x (where w=wm, x=secret attribute value)
    total_rm = [[(total_wm[i][j] - c*all_enc_attr[i][j]) % o for j in range(len(total_wm[i]))] for i in range(len(all_enc_attr))]

    # --- Final Result ---
    # The proof pi is the tuple (challenge, list_of_responses)
    return (c, total_rm)