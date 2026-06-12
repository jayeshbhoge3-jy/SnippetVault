import { Hero } from './components/sections/Hero';
import { Features } from './components/sections/Features';
import { Pricing } from './components/sections/Pricing';

function App() {
  return (
    <div className="min-h-screen bg-black text-[#E1E0CC] selection:bg-primary/30">
      <Hero />
      <Features />
      <Pricing />
    </div>
  );
}

export default App;
