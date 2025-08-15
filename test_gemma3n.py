import asyncio
from GEMMA3N_COLAB_INTEGRATION import Gemma3NIntegratedSystem
import numpy as np

async def test():
    print('🚀 Testing Gemma3N Integration in Mock Mode')
    print('='*60)
    
    system = Gemma3NIntegratedSystem()
    await system.setup(None)  # Mock mode
    
    # Test with sample audio
    audio = np.random.randn(8000) * 0.1
    result = await system.process_customer_query(audio)
    
    print(f"\n✅ System works!")
    print(f"  Model: {result['model_used']}")
    print(f"  Emotion: {result['emotion']['emotion']}")
    print(f"  Response: {result['model_response'][:100]}")
    
asyncio.run(test())
