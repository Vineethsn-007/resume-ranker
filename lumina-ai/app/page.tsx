import Header from "@/components/Header";
import Hero from "@/components/Hero";
import MethodologySection from "@/components/MethodologySection";
import SandboxSection from "@/components/SandboxSection";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <MethodologySection />
        <SandboxSection />
      </main>
      <Footer />
    </>
  );
}
