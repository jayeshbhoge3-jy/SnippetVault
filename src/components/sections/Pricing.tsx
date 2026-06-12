import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { Check } from 'lucide-react';
import { WordsPullUpMultiStyle } from '../ui/WordsPullUpMultiStyle';

export function Pricing() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: "-100px" });

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: (custom: number) => ({
      opacity: 1,
      scale: custom === 1 ? 1.02 : 1, // Make pro card slightly larger
      transition: {
        delay: custom * 0.15,
        duration: 0.6,
        ease: [0.22, 1, 0.36, 1] as [number, number, number, number]
      }
    })
  };

  const headerSegments = [
    { text: "Simple pricing for every developer.", className: "text-[#E1E0CC] text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-normal w-full" },
    { text: "No hidden fees. Cancel anytime.", className: "text-gray-500 text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal w-full mt-2" }
  ];

  return (
    <section id="pricing" className="w-full bg-black py-24 px-4 md:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16 md:mb-24 flex flex-col items-center">
          <WordsPullUpMultiStyle segments={headerSegments} className="flex-col items-center" />
        </div>

        <div 
          ref={containerRef}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8 items-center"
        >
          {/* Free Card */}
          <motion.div
            custom={0}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={cardVariants}
            className="bg-[#101010] rounded-2xl p-8 flex flex-col h-full"
          >
            <div className="mb-8">
              <span className="inline-block px-3 py-1 bg-[#212121] text-primary text-xs rounded-full mb-6">
                Free Forever
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-medium text-[#E1E0CC]">₹0</span>
                <span className="text-gray-500">/month</span>
              </div>
            </div>
            
            <ul className="space-y-4 mb-12 flex-grow">
              {["50 snippets max", "Public snippets", "Syntax highlighting", "Basic search", "GitHub OAuth login"].map((feature, i) => (
                <li key={i} className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-primary shrink-0" />
                  <span className="text-gray-400">{feature}</span>
                </li>
              ))}
            </ul>
            
            <button className="w-full py-3 rounded-full border border-primary/30 text-primary font-medium hover:bg-primary/10 transition-colors">
              Get Started Free
            </button>
          </motion.div>

          {/* Pro Card */}
          <motion.div
            custom={1}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={cardVariants}
            className="bg-[#DEDBC8] rounded-2xl p-8 flex flex-col h-full relative z-10 shadow-2xl shadow-primary/5"
          >
            <div className="mb-8">
              <span className="inline-block px-3 py-1 bg-black/20 text-black text-xs rounded-full mb-6 font-medium">
                Most Popular
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-medium text-black">₹299</span>
                <span className="text-black/60">/month</span>
              </div>
            </div>
            
            <ul className="space-y-4 mb-12 flex-grow">
              {["Unlimited snippets", "Private snippets", "Team sharing", "Advanced search + filters", "Priority support"].map((feature, i) => (
                <li key={i} className="flex items-center gap-3">
                  <Check className="w-5 h-5 text-black shrink-0" />
                  <span className="text-black/80 font-medium">{feature}</span>
                </li>
              ))}
            </ul>
            
            <button className="w-full py-3 rounded-full bg-black text-primary font-medium hover:bg-black/80 transition-colors">
              Start Pro
            </button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
