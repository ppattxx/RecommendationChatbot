/**
 * LandingPage — LombokEats
 * Structured with: Navbar → Hero → TopPicks → Footer
 */
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import TopPicksSection from '../components/TopPicksSection';
import Footer from '../components/Footer';

const LandingPage = ({ onOpenChat, onViewDetail }) => {
  return (
    <div className="min-h-screen bg-white">
      <Navbar onOpenChat={onOpenChat} />
      <HeroSection onOpenChat={onOpenChat} />
      <TopPicksSection onViewDetail={onViewDetail} />
      <Footer />
    </div>
  );
};

export default LandingPage;
