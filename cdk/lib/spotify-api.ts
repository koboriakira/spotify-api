/** @format */

import {
  Stack,
  StackProps,
  Duration,
  RemovalPolicy,
  aws_lambda as lambda,
  aws_iam as iam,
  aws_apigateway as apigateway,
  aws_s3 as s3,
  aws_events as events,
  aws_events_targets as targets,
} from "aws-cdk-lib";
import { Construct } from "constructs";

// CONFIG
const RUNTIME = lambda.Runtime.PYTHON_3_11;
const TIMEOUT = 30;
const APP_DIR_PATH = "../spotify_api";
const HANDLER_NAME = "main.handler";
const LAYER_ZIP_PATH = "../dependencies.zip";

export class SpotifyApi extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // S3バケットを作成
    const bucket = new s3.Bucket(this, "SpotifyApiBucket", {
      bucketName: "spotify-api-bucket-koboriakira",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // ロールを作成
    const role = this.makeRole(bucket.bucketArn);

    // レイヤーを作成
    const myLayer = this.makeLayer();

    // Lambda: main
    const fn = this.createLambdaFunction(
      "Lambda",
      "main.handler",
      role,
      myLayer,
      true
    );
    this.makeApiGateway(fn);

    // Lambda: notificate_current_playing
    const notificate_current_playing = this.createLambdaFunction(
      "notificate_current_playing",
      "notificate_current_playing.handler",
      role,
      myLayer
    );
    // new events.Rule(this, "notificate_current_playing", {
    //   schedule: events.Schedule.cron({ minute: "0/1" }), // 毎分実行
    //   targets: [
    //     new targets.LambdaFunction(notificate_current_playing, {
    //       retryAttempts: 1,
    //     }),
    //   ],
    // });
  }

  /**
   * Create or retrieve an IAM role for the Lambda function.
   * @returns {iam.Role} The created or retrieved IAM role.
   */
  makeRole(bucketArn: string) {
    // Lambda の実行ロールを作成
    const role = new iam.Role(this, "LambdaRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    // 管理ポリシーを追加
    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole"
      )
    );

    // ユーザポリシーを追加
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:InvokeFunction", "lambda:InvokeAsync"],
        resources: ["*"],
      })
    );
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["s3:*"],
        resources: [bucketArn + "/*"],
      })
    );

    return role;
  }

  /**
   * Create or retrieve a Lambda layer.
   * @returns {lambda.LayerVersion} The created or retrieved Lambda layer.
   */
  makeLayer() {
    return new lambda.LayerVersion(this, "Layer", {
      code: lambda.Code.fromAsset(LAYER_ZIP_PATH), // レイヤーの内容を含むディレクトリ
      compatibleRuntimes: [RUNTIME], // このレイヤーが互換性を持つランタイム
    });
  }

  /**
   * Create a Lambda function.
   * @param {iam.Role} role The IAM role for the Lambda function.
   * @param {lambda.LayerVersion} myLayer The Lambda layer to be used.
   * @returns {lambda.Function} The created Lambda function.
   */
  createLambdaFunction(
    name: string,
    handler_name: string,
    role: iam.Role,
    myLayer: lambda.LayerVersion,
    function_url_enabled: boolean = false
  ): lambda.Function {
    const fn = new lambda.Function(this, name, {
      runtime: RUNTIME,
      handler: handler_name,
      code: lambda.Code.fromAsset(APP_DIR_PATH),
      role: role,
      layers: [myLayer],
      timeout: Duration.seconds(TIMEOUT),
    });

    fn.addEnvironment("SPOTIFY_CLIENT_ID", process.env.SPOTIFY_CLIENT_ID || "");
    fn.addEnvironment(
      "SPOTIFY_CLIENT_SECRET",
      process.env.SPOTIFY_CLIENT_SECRET || ""
    );
    fn.addEnvironment("SLACK_BOT_TOKEN", process.env.SLACK_BOT_TOKEN || "");

    if (function_url_enabled) {
      fn.addFunctionUrl({
        authType: lambda.FunctionUrlAuthType.NONE, // 認証なし
      });
    }

    return fn;
  }

  /**
   * Create an API Gateway.
   * @param {lambda.Function} fn The Lambda function to be integrated.
   */
  makeApiGateway(fn: lambda.Function) {
    // REST API の定義
    const restapi = new apigateway.RestApi(this, "SpotifyApi", {
      deployOptions: {
        stageName: "v1",
      },
      restApiName: "SpotifyApi",
    });
    // ルートとインテグレーションの設定
    restapi.root.addMethod("ANY", new apigateway.LambdaIntegration(fn));
    restapi.root
      .addResource("{proxy+}")
      .addMethod("GET", new apigateway.LambdaIntegration(fn));
    return restapi;
  }
}
