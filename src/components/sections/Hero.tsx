import { ArrowRight } from 'lucide-react';
import { WordsPullUp } from '../ui/WordsPullUp';
import { motion } from 'framer-motion';

export function Hero() {
  const navItems = ['Home', 'Features', 'Pricing', 'Docs', 'GitHub'];

  return (
    <section className="h-screen w-full p-4 md:p-6 bg-black">
      <div className="relative w-full h-full rounded-2xl md:rounded-[2rem] overflow-hidden bg-[#101010]">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1555066931-4365d14bab8c")' }}
        />
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/60" />
        {/* Noise Overlay */}
        <div className="absolute inset-0 noise-overlay opacity-[0.7] mix-blend-overlay pointer-events-none" />

        {/* Navbar */}
        <nav className="absolute top-0 left-1/2 -translate-x-1/2 bg-black rounded-b-2xl md:rounded-b-3xl px-4 py-2 md:px-8 z-10 flex items-center gap-3 sm:gap-6 md:gap-12 lg:gap-14">
          {navItems.map((item) => (
            <a 
              key={item} 
              href={`#${item.toLowerCase()}`}
              className="text-[10px] sm:text-xs md:text-sm text-[#E1E0CC]/80 hover:text-[#E1E0CC] transition-colors"
            >
              {item}
            </a>
          ))}
        </nav>

        {/* Hero Content */}
        <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-8 md:p-12 z-10">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-end">
            <div className="md:col-span-8">
              <WordsPullUp 
                text="SnippetVault"
                className="text-[14vw] sm:text-[13vw] md:text-[12vw] lg:text-[11vw] font-medium leading-[0.85] tracking-[-0.07em] text-[#E1E0CC] justify-start"
                showAsterisk={true}
              />
            </div>
            
            <div className="md:col-span-4 flex flex-col items-start md:items-end md:text-right gap-6">
              <motion.p 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="text-primary/70 text-xs sm:text-sm md:text-base leading-[1.2] max-w-sm"
              >
                SnippetVault is your personal code library — store, organize, 
                and share snippets across every language and framework. 
                Built for developers who value speed and clarity.
              </motion.p>
              
              <motion.button
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.7, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="group flex items-center gap-2 bg-primary rounded-full pl-6 pr-2 py-2 text-black font-medium hover:gap-3 transition-all duration-300"
              >
                <span>Start for Free</span>
                <span className="flex items-center justify-center bg-black rounded-full w-9 h-9 group-hover:scale-110 transition-transform duration-300">
                  <ArrowRight className="w-4 h-4 text-[#E1E0CC]" />
                </span>
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
