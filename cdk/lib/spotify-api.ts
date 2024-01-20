/** @format */

import {
  Stack,
  StackProps,
  Duration,
  aws_lambda as lambda,
  aws_iam as iam,
  aws_apigateway as apigateway,
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

    const role = this.makeRole();
    const myLayer = this.makeLayer();
    const fn = this.createLambdaFunction(role, myLayer);
    this.makeApiGateway(fn);
  }

  /**
   * Create or retrieve an IAM role for the Lambda function.
   * @returns {iam.Role} The created or retrieved IAM role.
   */
  makeRole() {
    // Lambdaの実行ロールを取得または新規作成
    const role = new iam.Role(this, "LambdaRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    // Lambda の実行ロールに管理ポリシーを追加
    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole"
      )
    );

    // 必要に応じて追加の権限をポリシーとしてロールに付与
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:InvokeFunction", "lambda:InvokeAsync"],
        resources: ["*"],
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
    role: iam.Role,
    myLayer: lambda.LayerVersion
  ): lambda.Function {
    const fn = new lambda.Function(this, "Lambda", {
      runtime: RUNTIME,
      handler: HANDLER_NAME,
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

    fn.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // 認証なし
    });

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