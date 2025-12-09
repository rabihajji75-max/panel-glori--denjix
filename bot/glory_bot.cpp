#include <iostream>
#include <thread>
#include <chrono>
#include <string>
#include <map>
#include <atomic>
#include <random>

class GloryBot {
private:
    std::string token;
    std::string clan_id;
    std::atomic<bool> running;
    int glory_collected;
    
public:
    GloryBot(const std::string& token, const std::string& clan_id = "")
        : token(token), clan_id(clan_id), running(false), glory_collected(0) {}
    
    bool start() {
        if (running) return false;
        
        running = true;
        std::cout << "Starting bot for token: " << token.substr(0, 10) << "..." << std::endl;
        
        // Connect to game (simulated)
        if (!connect_to_game()) {
            std::cout << "Failed to connect to game" << std::endl;
            return false;
        }
        
        // Start glory collection in separate thread
        std::thread([this]() {
            collect_glory_loop();
        }).detach();
        
        return true;
    }
    
    bool connect_to_game() {
        // Simulated connection
        std::this_thread::sleep_for(std::chrono::seconds(2));
        std::cout << "Connected to game server" << std::endl;
        return true;
    }
    
    void collect_glory_loop() {
        while (running) {
            try {
                // Simulate playing a match
                simulate_match();
                
                // Collect glory
                int glory = collect_glory();
                glory_collected += glory;
                
                std::cout << "Collected " << glory << " glory. Total: " << glory_collected << std::endl;
                
                // Wait before next match
                std::this_thread::sleep_for(std::chrono::minutes(5));
                
            } catch (const std::exception& e) {
                std::cout << "Error in glory loop: " << e.what() << std::endl;
                std::this_thread::sleep_for(std::chrono::minutes(1));
            }
        }
    }
    
    void simulate_match() {
        std::cout << "Simulating match..." << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(30));
        std::cout << "Match completed" << std::endl;
    }
    
    int collect_glory() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dist(50, 150);
        return dist(gen);
    }
    
    bool send_clan_request() {
        if (clan_id.empty()) return false;
        
        std::cout << "Sending clan request to: " << clan_id << std::endl;
        // Simulated API call
        std::this_thread::sleep_for(std::chrono::seconds(2));
        return true;
    }
    
    void stop() {
        running = false;
        std::cout << "Bot stopped. Total glory: " << glory_collected << std::endl;
    }
    
    int get_glory_collected() const {
        return glory_collected;
    }
};

class BotManager {
private:
    std::map<std::string, GloryBot*> bots;
    
public:
    ~BotManager() {
        stop_all();
    }
    
    void add_bot(const std::string& account_id, const std::string& token, const std::string& clan_id = "") {
        bots[account_id] = new GloryBot(token, clan_id);
    }
    
    bool start_bot(const std::string& account_id) {
        auto it = bots.find(account_id);
        if (it != bots.end()) {
            return it->second->start();
        }
        return false;
    }
    
    bool stop_bot(const std::string& account_id) {
        auto it = bots.find(account_id);
        if (it != bots.end()) {
            it->second->stop();
            delete it->second;
            bots.erase(it);
            return true;
        }
        return false;
    }
    
    void start_all() {
        for (auto& pair : bots) {
            pair.second->start();
        }
    }
    
    void stop_all() {
        for (auto& pair : bots) {
            pair.second->stop();
            delete pair.second;
        }
        bots.clear();
    }
};

int main() {
    BotManager manager;
    
    // Add sample bots
    manager.add_bot("account1", "token123", "clan_456");
    manager.add_bot("account2", "token456", "clan_789");
    
    // Start all bots
    manager.start_all();
    
    // Run for 1 minute
    std::this_thread::sleep_for(std::chrono::minutes(1));
    
    // Stop all bots
    manager.stop_all();
    
    return 0;
}
