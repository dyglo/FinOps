'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, CreditCard, Smartphone, Store, Wallet, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export default function HomePage() {
  return (
    <div className="flex flex-col gap-32 pb-20 pt-16">
      {/* HERO SECTION */}
      <section className="relative grid lg:grid-cols-2 gap-12 items-center">
        <div className="flex flex-col gap-8 max-w-xl">
          <div className="flex flex-col gap-2">
            <h1 className="text-[84px] font-bold leading-[1.05] tracking-tight text-black dark:text-white transition-colors">
              Intelligence <br />
              Done <span className="inline-flex items-center -translate-y-2"><CircleIcon /></span> <br /> 
              Smoothly
            </h1>
          </div>
          <p className="text-lg text-gray-500 dark:text-zinc-400 max-w-md leading-relaxed transition-colors">
            With this platform you can manage all your finance intelligence and agentic workflows very easily & fast.
          </p>
          <div className="flex items-center gap-6">
            <Link href="/dashboard">
              <Button size="lg" className="bg-black dark:bg-white text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 btn-pill px-8 h-14 text-base">
                Get Started
              </Button>
            </Link>
            <div className="relative h-20 w-20 flex items-center justify-center">
               <div className="absolute inset-0 animate-spin-slow">
                 <svg viewBox="0 0 100 100" className="h-full w-full">
                   <path id="curve" d="M 50, 50 m -37, 0 a 37,37 0 1,1 74,0 a 37,37 0 1,1 -74,0" fill="transparent" />
                   <text className="text-[10px] uppercase tracking-widest font-bold fill-black dark:fill-white transition-colors">
                     <textPath xlinkHref="#curve">Try it for free • Try it for free • </textPath>
                   </text>
                 </svg>
               </div>
               <div className="h-10 w-10 bg-lime-300 dark:bg-lime-400 rounded-full flex items-center justify-center text-black">
                 <ArrowRight className="h-5 w-5" />
               </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 pt-4">
            <p className="text-sm font-medium text-gray-400 dark:text-zinc-500">Over <span className="text-black dark:text-white transition-colors">13,000+ Client</span> all over the world</p>
            <div className="flex -space-x-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-10 w-10 rounded-full border-2 border-white dark:border-zinc-900 bg-gray-200 dark:bg-zinc-800 overflow-hidden relative">
                  <Image src={`https://i.pravatar.cc/100?u=${i}`} alt="user" fill className="object-cover" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* FLOATING CARDS AREA */}
        <div className="relative h-[600px] w-full hidden lg:block">
           {/* Card: Sent to */}
           <motion.div
             initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}   
             className="absolute top-0 right-32 w-64 glass-card rounded-3xl p-6 z-20"
           >
             <div className="flex justify-between items-center mb-4">
               <span className="font-bold text-sm">Sent to</span>
               <span className="text-[10px] text-gray-400 dark:text-zinc-500 font-bold uppercase">View All</span>
             </div>
             <div className="flex gap-3">
                {[1,2,3,4].map(i => (
                  <div key={i} className="h-10 w-10 rounded-full bg-gray-100 dark:bg-zinc-800 border border-white dark:border-zinc-700" />      
                ))}
             </div>
             <div className="mt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30" />
                    <div className="flex flex-col"><span className="text-xs font-bold">Amazon</span><span className="text-[10px] text-gray-400">Payment</span></div>
                  </div>
                  <span className="text-xs font-bold">$12.44</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/30" />
                    <div className="flex flex-col"><span className="text-xs font-bold">Turkcell</span><span className="text-[10px] text-gray-400">Subscription</span></div>
                  </div>
                  <span className="text-xs font-bold">$44.00</span>
                </div>
             </div>
           </motion.div>

           {/* Card: Paypal */}
           <motion.div
             initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.4 }}   
             className="absolute top-20 right-0 w-48 bg-purple-200 dark:bg-purple-900/40 rounded-3xl p-6 z-10 text-black dark:text-white"
           >
             <Smartphone className="h-6 w-6 mb-4" />
             <p className="text-xs font-bold opacity-60">Paypal</p>
             <p className="text-[10px] opacity-40 mb-4 font-mono">Jul 09, 2022</p>
             <p className="text-2xl font-bold font-mono tracking-tighter">$3502</p>
           </motion.div>

           {/* Card: Profile */}
           <motion.div
             initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.6 }}  
             className="absolute bottom-40 right-40 w-56 bg-lime-300 dark:bg-lime-400 text-black rounded-3xl p-6 z-30"
           >
             <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-full bg-black/10 dark:bg-black/20" />
                <div className="flex flex-col"><span className="text-xs font-bold">Hello Robert,</span><span className="text-[10px] font-bold">Welcome back</span></div>
             </div>
             <div className="flex gap-4">
                <div className="flex flex-col gap-1">
                  <div className="h-10 w-10 rounded-xl bg-black flex items-center justify-center text-white"><Wallet className="h-5 w-5" /></div>
                  <span className="text-[10px] font-bold font-mono">$1327</span>
                </div>
                <div className="flex flex-col gap-1">
                  <div className="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-black"><CreditCard className="h-5 w-5" /></div>
                  <span className="text-[10px] font-bold font-mono">$3502</span>
                </div>
             </div>
           </motion.div>

           {/* Card: Visa */}
           <motion.div
             initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.8 }}   
             className="absolute bottom-10 right-0 w-64 bg-zinc-900 dark:bg-zinc-950 text-white rounded-3xl p-6 z-20 border border-white/10"      
           >
             <div className="flex justify-between items-start mb-8">
               <div className="flex flex-col"><span className="text-[10px] opacity-60 font-bold">VISA</span><span className="text-[10px] opacity-40 font-bold uppercase tracking-widest">Debit</span></div>
               <div className="h-6 w-10 rounded bg-white/10" />
             </div>
             <p className="text-lg font-mono tracking-widest mb-4">$25,750.50</p>
             <div className="flex justify-between items-center text-[10px] opacity-60 font-bold font-mono">
                <span>05/28</span>
                <span>4512 ••••</span>
             </div>
           </motion.div>

           {/* Card: Floating Gradient Card */}
           <motion.div
             initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 1 }}
             className="absolute bottom-20 left-20 w-44 h-56 bg-gradient-to-br from-rose-200 via-orange-100 to-amber-100 dark:from-rose-900/40 dark:via-orange-900/40 dark:to-amber-900/40 text-black dark:text-white rounded-3xl p-6 -rotate-6 shadow-xl border border-white/10"
           >
              <div className="h-8 w-8 rounded-full bg-white/20 dark:bg-black/20 mb-12" />
              <p className="text-[10px] font-bold opacity-60">Card number</p>
              <p className="text-xs font-bold mb-4 font-mono">5737 ••••</p>
              <p className="text-[10px] font-bold opacity-60">Name</p>
              <p className="text-xs font-bold">Madhu Ma</p>
           </motion.div>

           <div className="absolute top-1/2 left-0 transform -translate-y-1/2 text-black/5 dark:text-white/5">
              <SparkleIcon className="h-12 w-12" />
           </div>
        </div>
      </section>

      {/* SERVICES SECTION */}
      <section className="flex flex-col items-center gap-16">
        <div className="text-center space-y-4">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 dark:text-zinc-600 transition-colors">Take a look at Services</p>
          <h2 className="text-5xl font-bold text-black dark:text-white tracking-tight transition-colors">We provide Services</h2>
        </div>

        <div className="w-full max-w-4xl">
           <div className="flex flex-wrap justify-center gap-4 mb-16">
              <ServiceTab active icon={<CreditCard className="h-5 w-5" />} label="Credit Card" />
              <ServiceTab icon={<Smartphone className="h-5 w-5" />} label="Debit Card" />
              <ServiceTab icon={<Store className="h-5 w-5" />} label="Debit Store Card" />
              <ServiceTab icon={<Smartphone className="h-5 w-5" />} label="Payment App" />
           </div>

           <div className="grid md:grid-cols-2 gap-20 items-center">
              <div className="space-y-8">
                <h3 className="text-3xl font-bold leading-tight text-black dark:text-white transition-colors">
                  Our best fintech solution additional optimization to make running.
                </h3>
                <p className="text-gray-500 dark:text-zinc-400 leading-relaxed transition-colors">
                  We are top class worldwide solution additional optimization to make running fintech online services. We are dedicate to work with our customers.
                </p>
                <div className="grid grid-cols-2 gap-y-4 gap-x-8">
                   <FeatureItem label="Buy anything anywhere" />
                   <FeatureItem label="Accept Payment" />
                   <FeatureItem label="Connect your wallet" />
                   <FeatureItem label="Payment request" />
                   <FeatureItem label="Use Apple Pay" />
                   <FeatureItem label="Shop Online" />
                   <FeatureItem label="Earn Card Points" />
                   <FeatureItem label="Easy Shopping" />
                </div>
              </div>
              <div className="relative h-80 rounded-[40px] bg-gray-50 dark:bg-zinc-900 border border-gray-100 dark:border-zinc-800 overflow-hidden transition-colors">
                 <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-50 dark:from-blue-900/10 to-transparent" />
                 <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-40 glass-card rounded-2xl flex items-center justify-center">
                    <CreditCard className="h-12 w-12 text-black/10 dark:text-white/10" />
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="flex flex-col items-center gap-16">
        <div className="text-center space-y-4">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 dark:text-zinc-600 transition-colors">Client Testimonial</p>
          <h2 className="text-5xl font-bold text-black dark:text-white tracking-tight transition-colors">What they say about</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-8 w-full">
           {[1,2,3].map(i => (
             <Card key={i} className="border-none shadow-none bg-white/50 dark:bg-zinc-900/50 p-10 rounded-[40px] space-y-6 transition-colors">
                <span className="text-6xl font-serif text-black/10 dark:text-white/10">“</span>
                <p className="text-gray-500 dark:text-zinc-400 leading-relaxed italic transition-colors">
                  We are top class worldwide solution additional optimization to make running fintech online services.
                </p>
                <div className="flex items-center gap-4">
                   <div className="h-12 w-12 rounded-full bg-gray-200 dark:bg-zinc-800 transition-colors" />
                   <div className="flex flex-col"><span className="font-bold text-black dark:text-white transition-colors">Alex Pitter</span><span className="text-xs text-gray-400 dark:text-zinc-600 uppercase tracking-widest font-black">Director, HSBC Bank</span></div>
                </div>
             </Card>
           ))}
        </div>
      </section>

      {/* BLOG */}
      <section className="flex flex-col items-center gap-16 pb-20">
        <div className="text-center space-y-4">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 dark:text-zinc-600 transition-colors">Our Blog</p>
          <h2 className="text-5xl font-bold text-black dark:text-white tracking-tight transition-colors">Latest news from our blog</h2>
        </div>
        <div className="grid md:grid-cols-2 gap-8 w-full">
           <BlogCard image="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&q=80&w=800" title="Manage your fintech solution and type of solution are build." date="January 12, 2022" />
           <BlogCard image="https://images.unsplash.com/photo-1573163281538-507307adc2ff?auto=format&fit=crop&q=80&w=800" title="Build your great business site simply better." date="January 13, 2022" />
        </div>
      </section>
    </div>
  );
}

function CircleIcon() {
  return (
    <div className="flex -space-x-3">
       <div className="h-12 w-12 rounded-full border-4 border-black dark:border-white bg-white dark:bg-black flex items-center justify-center transition-colors">
          <div className="h-4 w-4 rounded-full bg-black dark:bg-white" />
       </div>
       <div className="h-12 w-12 rounded-full border-4 border-black dark:border-white bg-white dark:bg-black flex items-center justify-center transition-colors">
          <Check className="h-6 w-6 text-black dark:text-white" />
       </div>
    </div>
  )
}

function SparkleIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor">
      <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z" />
    </svg>
  )
}

function ServiceTab({ active, icon, label }: { active?: boolean, icon: React.ReactNode, label: string }) {
  return (
    <div className={cn(
      "flex items-center gap-3 px-8 py-5 rounded-2xl border transition-all cursor-pointer",
      active 
        ? "bg-white dark:bg-zinc-800 shadow-xl border-white dark:border-zinc-700 scale-105 text-black dark:text-white" 
        : "border-gray-100 dark:border-zinc-800 hover:border-gray-200 dark:hover:border-zinc-700 text-gray-400 dark:text-zinc-600"
    )}>
      {icon}
      <span className="font-bold text-sm">{label}</span>
    </div>
  )
}

function FeatureItem({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex-shrink-0 h-4 w-4 flex items-center justify-center rounded-full bg-black/5 dark:bg-white/5 transition-colors">
        <div className="h-1.5 w-1.5 rounded-full bg-black dark:bg-white transition-colors" />
      </div>
      <span className="text-xs font-bold text-gray-500 dark:text-zinc-400 transition-colors">{label}</span>
    </div>
  )
}

function BlogCard({ image, title, date }: { image: string, title: string, date: string }) {
  return (
    <div className="group cursor-pointer space-y-6">
       <div className="relative aspect-[16/9] rounded-[40px] overflow-hidden border border-gray-100 dark:border-zinc-800 transition-colors">
          <Image src={image} alt={title} fill className="object-cover transition-transform duration-500 group-hover:scale-110" />
       </div>
       <div className="space-y-2">
          <p className="text-xs font-bold text-gray-400 dark:text-zinc-600 uppercase tracking-widest transition-colors">{date}</p>
          <h4 className="text-2xl font-bold text-black dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors tracking-tight">{title}</h4>
       </div>
    </div>
  )
}