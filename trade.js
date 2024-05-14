const solanaWeb3 = require('@solana/web3.js');
const { Keypair, Connection, LAMPORTS_PER_SOL, PublicKey } = solanaWeb3;

// Connect to Solana network
const connection = new Connection("https://api.mainnet-beta.solana.com");

// Load your wallet's keypair (replace with your own keypair)
const keypair = Keypair.fromSecretKey(new Uint8Array([/* your keypair array here */]));

async function executeTrade(toPublicKeyString) {
    try {
        const toPublicKey = new PublicKey(toPublicKeyString);
        const transaction = new solanaWeb3.Transaction().add(
            solanaWeb3.SystemProgram.transfer({
                fromPubkey: keypair.publicKey,
                toPubkey: toPublicKey,
                lamports: LAMPORTS_PER_SOL / 100, // Adjust the amount to send
            })
        );

        // Sign and send the transaction
        const signature = await solanaWeb3.sendAndConfirmTransaction(
            connection,
            transaction,
            [keypair]
        );

        console.log("Transaction confirmed with signature:", signature);
    } catch (error) {
        console.error("Error executing trade:", error);
    }
}

// Example usage: Execute a trade to a given public key
executeTrade("recipientPublicKeyHere");
