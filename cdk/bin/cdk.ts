#!/usr/bin/env node
/** @format */

import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { SpotifyApi } from "../lib/spotify-api";

const app = new cdk.App();
new SpotifyApi(app, "SpotifyApi", {});
