<?php
/**
 * Plugin Name: Islamic AI Chat Widget
 * Plugin URI: https://theislaminsights.com
 * Description: Embeds the Islamic AI Assistant chat widget on your website
 * Version: 1.0.0
 * Author: TheIslamInsights.com
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class IslamicAIChatWidget {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'render_chat_widget'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'settings_init'));
    }
    
    public function init() {
        // Plugin initialization
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script(
            'islamic-ai-chat-widget',
            plugin_dir_url(__FILE__) . 'islamic-chat-widget.js',
            array(),
            '1.0.0',
            true
        );
        
        // Pass configuration to JavaScript
        $config = array(
            'apiUrl' => get_option('islamic_ai_api_url', 'http://localhost:5002'),
            'position' => get_option('islamic_ai_position', 'bottom-right'),
            'theme' => get_option('islamic_ai_theme', 'islamic-green'),
            'title' => get_option('islamic_ai_title', 'Islamic AI Assistant'),
            'subtitle' => get_option('islamic_ai_subtitle', 'Ask about Islam, Quran, Hadith & more')
        );
        
        wp_localize_script('islamic-ai-chat-widget', 'IslamicChatConfig', $config);
    }
    
    public function render_chat_widget() {
        // The widget will be automatically initialized by the JavaScript
        echo '<script>
            if (typeof IslamicChatWidget !== "undefined" && typeof IslamicChatConfig !== "undefined") {
                new IslamicChatWidget(IslamicChatConfig);
            }
        </script>';
    }
    
    public function add_admin_menu() {
        add_options_page(
            'Islamic AI Chat Settings',
            'Islamic AI Chat',
            'manage_options',
            'islamic-ai-chat',
            array($this, 'options_page')
        );
    }
    
    public function settings_init() {
        register_setting('islamic_ai_chat', 'islamic_ai_api_url');
        register_setting('islamic_ai_chat', 'islamic_ai_position');
        register_setting('islamic_ai_chat', 'islamic_ai_theme');
        register_setting('islamic_ai_chat', 'islamic_ai_title');
        register_setting('islamic_ai_chat', 'islamic_ai_subtitle');
        register_setting('islamic_ai_chat', 'islamic_ai_enabled');
        
        add_settings_section(
            'islamic_ai_chat_section',
            __('Islamic AI Chat Widget Settings', 'islamic-ai-chat'),
            array($this, 'settings_section_callback'),
            'islamic_ai_chat'
        );
        
        add_settings_field(
            'islamic_ai_enabled',
            __('Enable Chat Widget', 'islamic-ai-chat'),
            array($this, 'enabled_render'),
            'islamic_ai_chat',
            'islamic_ai_chat_section'
        );
        
        add_settings_field(
            'islamic_ai_api_url',
            __('API URL', 'islamic-ai-chat'),
            array($this, 'api_url_render'),
            'islamic_ai_chat',
            'islamic_ai_chat_section'
        );
        
        add_settings_field(
            'islamic_ai_position',
            __('Widget Position', 'islamic-ai-chat'),
            array($this, 'position_render'),
            'islamic_ai_chat',
            'islamic_ai_chat_section'
        );
        
        add_settings_field(
            'islamic_ai_title',
            __('Widget Title', 'islamic-ai-chat'),
            array($this, 'title_render'),
            'islamic_ai_chat',
            'islamic_ai_chat_section'
        );
        
        add_settings_field(
            'islamic_ai_subtitle',
            __('Widget Subtitle', 'islamic-ai-chat'),
            array($this, 'subtitle_render'),
            'islamic_ai_chat',
            'islamic_ai_chat_section'
        );
    }
    
    public function enabled_render() {
        $enabled = get_option('islamic_ai_enabled', '1');
        ?>
        <input type='checkbox' name='islamic_ai_enabled' <?php checked($enabled, 1); ?> value='1'>
        <p class="description">Check to enable the Islamic AI chat widget on your website.</p>
        <?php
    }
    
    public function api_url_render() {
        $api_url = get_option('islamic_ai_api_url', 'http://localhost:5002');
        ?>
        <input type='text' name='islamic_ai_api_url' value='<?php echo esc_attr($api_url); ?>' size='50'>
        <p class="description">Enter the URL of your Islamic AI API server (e.g., https://your-api-server.com)</p>
        <?php
    }
    
    public function position_render() {
        $position = get_option('islamic_ai_position', 'bottom-right');
        ?>
        <select name='islamic_ai_position'>
            <option value='bottom-right' <?php selected($position, 'bottom-right'); ?>>Bottom Right</option>
            <option value='bottom-left' <?php selected($position, 'bottom-left'); ?>>Bottom Left</option>
        </select>
        <p class="description">Choose where to display the chat widget on your website.</p>
        <?php
    }
    
    public function title_render() {
        $title = get_option('islamic_ai_title', 'Islamic AI Assistant');
        ?>
        <input type='text' name='islamic_ai_title' value='<?php echo esc_attr($title); ?>' size='30'>
        <p class="description">Title displayed in the chat widget header.</p>
        <?php
    }
    
    public function subtitle_render() {
        $subtitle = get_option('islamic_ai_subtitle', 'Ask about Islam, Quran, Hadith & more');
        ?>
        <input type='text' name='islamic_ai_subtitle' value='<?php echo esc_attr($subtitle); ?>' size='50'>
        <p class="description">Subtitle displayed in the chat widget header.</p>
        <?php
    }
    
    public function settings_section_callback() {
        echo __('Configure your Islamic AI Chat Widget settings below:', 'islamic-ai-chat');
    }
    
    public function options_page() {
        ?>
        <div class="wrap">
            <h1>🕌 Islamic AI Chat Widget Settings</h1>
            <form action='options.php' method='post'>
                <?php
                settings_fields('islamic_ai_chat');
                do_settings_sections('islamic_ai_chat');
                submit_button();
                ?>
            </form>
            
            <div style="margin-top: 30px; padding: 20px; background: #f1f1f1; border-radius: 5px;">
                <h3>📋 Setup Instructions</h3>
                <ol>
                    <li><strong>Deploy your Islamic AI API:</strong> Make sure your Islamic AI backend is running and accessible via HTTPS.</li>
                    <li><strong>Update API URL:</strong> Enter your API server URL in the field above.</li>
                    <li><strong>Enable the widget:</strong> Check the "Enable Chat Widget" option.</li>
                    <li><strong>Customize appearance:</strong> Adjust the title, subtitle, and position as needed.</li>
                    <li><strong>Save settings:</strong> Click "Save Changes" to apply your configuration.</li>
                </ol>
                
                <h3>🔧 Technical Requirements</h3>
                <ul>
                    <li>Your Islamic AI API server must be running and accessible</li>
                    <li>CORS must be configured to allow requests from your domain</li>
                    <li>HTTPS is recommended for production use</li>
                </ul>
                
                <h3>🆘 Support</h3>
                <p>For support and documentation, visit <a href="https://theislaminsights.com" target="_blank">TheIslamInsights.com</a></p>
            </div>
        </div>
        <?php
    }
}

// Initialize the plugin
new IslamicAIChatWidget();

// Activation hook
register_activation_hook(__FILE__, 'islamic_ai_chat_activate');
function islamic_ai_chat_activate() {
    // Set default options
    add_option('islamic_ai_enabled', '1');
    add_option('islamic_ai_api_url', 'http://localhost:5002');
    add_option('islamic_ai_position', 'bottom-right');
    add_option('islamic_ai_theme', 'islamic-green');
    add_option('islamic_ai_title', 'Islamic AI Assistant');
    add_option('islamic_ai_subtitle', 'Ask about Islam, Quran, Hadith & more');
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'islamic_ai_chat_deactivate');
function islamic_ai_chat_deactivate() {
    // Clean up if needed
}
?>
