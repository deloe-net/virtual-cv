const CopyPlugin = require("copy-webpack-plugin");
const webpack = require('webpack');

module.exports = [
   {
        entry: './webapp/assets/src/home.js',
        mode: process.env.NODE_ENV,
        output: {
                path: `${__dirname}/webapp/assets/dist/`,
                filename: 'home.bundle.js'
            },
        module: {
            rules: [
                        {
                          test: /(home|cookie_notice)\.css$/,
                          use: [
                            'style-loader',
                            'css-loader'
                          ],
                        },
                    ],
            },
        resolve: {
            alias: {
                    locales: `${__dirname}/webapp/assets/src/locales/home`,
                },
            },
        plugins: [
                new CopyPlugin({
                  patterns: [
                    {
                        from: "webapp/assets/src/locales/home/",
                        to: "locales/home/"
                    },
                  ],
                }),
                new webpack.EnvironmentPlugin({
                    "TS_G_ANALYTICS_ID": process.env.TS_G_ANALYTICS_ID,
                }),
        ],
    },
   {
        entry: './webapp/assets/src/tac.js',
        mode: process.env.NODE_ENV,
        output: {
                path: `${__dirname}/webapp/assets/dist/`,
                filename: 'tac.bundle.js'
            },
        module: {
            rules: [
                        {
                          test: /(tac|cookie_notice)\.css$/,
                          use: [
                            'style-loader',
                            'css-loader'
                          ],
                        },
                    ],
            },
        plugins: [
          new webpack.EnvironmentPlugin({
            "TS_G_ANALYTICS_ID": process.env.TS_G_ANALYTICS_ID,
          } ),
        ],

    },
   {
        entry: './webapp/assets/src/errors.js',
        mode: process.env.NODE_ENV,
        output: {
                path: `${__dirname}/webapp/assets/dist/`,
                filename: 'errors.bundle.js'
            },
        module: {
            rules: [
                        {
                          test: /errors\.css$/,
                          use: [
                            'style-loader',
                            'css-loader'
                          ],
                        },
                    ],
            },
        resolve: {
            alias: {
                    locales: `${__dirname}/webapp/assets/src/locales/errors`,
                },
            },
        plugins: [
          new webpack.EnvironmentPlugin({
            "TS_G_ANALYTICS_ID": process.env.TS_G_ANALYTICS_ID,
          } ),
        ],

    },
   {
        entry: './webapp/assets/src/privacy.js',
        mode: process.env.NODE_ENV,
        output: {
                path: `${__dirname}/webapp/assets/dist/`,
                filename: 'privacy.bundle.js'
            },
        module: {
            rules: [
                        {
                          test: /(privacy|rocket)\.css$/,
                          use: [
                            'style-loader',
                            'css-loader'
                          ],
                        },
                    ],
            },
        plugins: [
          new webpack.EnvironmentPlugin({
            "TS_G_ANALYTICS_ID": process.env.TS_G_ANALYTICS_ID,
          } ),
        ],
    },
   {
        entry: './webapp/assets/src/auth.js',
        mode: process.env.NODE_ENV,
        output: {
                path: `${__dirname}/webapp/assets/dist/`,
                filename: 'auth.bundle.js'
            },
        module: {
            rules: [
                        {
                          test: /(auth|cookie_notice)\.css$/,
                          use: [
                            'style-loader',
                            'css-loader'
                          ],
                        },
                    ],
            },
        resolve: {
            alias: {
                    locales: `${__dirname}/webapp/assets/src/locales/auth`,
                },
            },
        plugins: [
                new CopyPlugin({
                  patterns: [
                    {
                        from: "webapp/assets/src/multimedia/images/avtar.png",
                        to: "multimedia/images/avtar.png"
                    },
                    {
                        from: "webapp/assets/src/multimedia/images/favicon.ico",
                        to: "multimedia/images/favicon.ico"
                    },
                    {
                        from: "webapp/assets/src/locales/auth/",
                        to: "locales/auth/"
                    },
                  ],
                }),
                new webpack.EnvironmentPlugin({
                    "TS_G_ANALYTICS_ID": process.env.TS_G_ANALYTICS_ID,
                    "TS_RECAPTCHA_PUBLIC_KEY": process.env.TS_RECAPTCHA_PUBLIC_KEY,
                  } ),
            ],
    },
];
