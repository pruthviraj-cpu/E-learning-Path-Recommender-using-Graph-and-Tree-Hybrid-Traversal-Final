import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import * as feather from "feather-icons";

const Navbar = () => {
  const location = useLocation();
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('userData');
    if (storedUser) {
      setUserData(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    feather.replace();
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem('userData');
    localStorage.removeItem('currentLearningPath');
    window.location.href = '/login';
  };

  const getUserInitial = () => {
    if (userData?.name) {
      return userData.name.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-2">
            <i data-feather="compass" className="text-blue-600"></i>
            <h1 className="text-xl font-bold text-gray-800">LearnPath</h1>
          </div>
          <nav className="hidden md:flex space-x-6">
            <Link 
              to="/" 
              className={`font-medium ${isActive('/') ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-blue-600'}`}
            >
              Dashboard
            </Link>
            <Link 
              to="/pathways" 
              className={`font-medium ${isActive('/pathways') ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-blue-600'}`}
            >
              My Pathways
            </Link>
            <Link 
              to="/learning" 
              className={`font-medium ${isActive('/learning') ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-blue-600'}`}
            >
              Learning
            </Link>
            <Link 
              to="/onboarding" 
              className={`font-medium ${isActive('/onboarding') ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : 'text-gray-600 hover:text-blue-600'}`}
            >
              Onboarding
            </Link>
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search..."
              className="pl-10 pr-4 py-2 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <i data-feather="search" className="absolute left-3 top-2.5 text-gray-400"></i>
          </div>
          <button className="p-2 rounded-full hover:bg-gray-100">
            <i data-feather="bell" className="text-gray-600"></i>
          </button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
              {getUserInitial()}
            </div>
            <span className="hidden md:inline text-sm font-medium">{userData?.name || 'User'}</span>
          </div>
          <button onClick={handleLogout} className="p-2 rounded-full hover:bg-gray-100">
            <i data-feather="log-out" className="text-gray-600"></i>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;